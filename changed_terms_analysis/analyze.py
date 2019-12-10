from collections import Counter
from contextlib import contextmanager
import concurrent.futures
import json
import os.path
import re
import sys
from tqdm import tqdm
from urllib.parse import urlparse
from web_monitoring import db
from web_monitoring.diff import differs
from .sqlite import sqlite_database, write_page_to_sqlite
from .terms import KEY_TERMS
from .tools import (CharacterToWordDiffs, changed_ngrams, load_url,
                    load_url_readability, parallel)


# Can Analyze? ----------------------------------------------------------------
# This script can only really handle HTML and HTML-like data.

REQUIRE_MEDIA_TYPE = False

# text/* media types are allowed, so only non-text types need be explicitly
# allowed and only text types need be explicitly disallowed.
ALLOWED_MEDIA = frozenset((
    # HTML should be text/html, but these are also common.
    'appliction/html',
    'application/xhtml',
    'application/xhtml+xml',
    'application/xml',
    'application/xml+html',
    'application/xml+xhtml'
))

DISALLOWED_MEDIA = frozenset((
    'text/calendar',
    'application/rss+xml'
))

# Extensions to check for if there's no available media type information.
DISALLOWED_EXTENSIONS = frozenset((
    '.jpg',
    '.pdf',
    '.athruz',
    '.avi',
    '.doc',
    '.docbook',
    '.docx',
    '.dsselect',
    '.eps',
    '.epub',
    '.exe',
    '.gif',
    '.jpeg',
    '.jpg',
    '.kmz',
    '.m2t',
    '.mov',
    '.mp3',
    '.mpg',
    '.pdf',
    '.png',
    '.ppt',
    '.pptx',
    '.radar',
    '.rtf',
    '.wmv',
    '.xls',
    '.xlsm',
    '.xlsx',
    '.xml',
    '.zip'
))


def is_fetchable(url):
    return url and (url.startswith('http:') or url.startswith('https:'))


def is_allowed_extension(url):
    extension = os.path.splitext(urlparse(url).path)[1]
    return not extension or extension not in DISALLOWED_EXTENSIONS


def is_analyzable_media(version):
    # In the future, the data from DB will have media type info surfaced in a
    # nice way, but it doesn't yet, so we need some logic. :(
    media = (version['source_metadata'].get('content_type') or
             version['source_metadata'].get('mime_type'))

    if media:
        media = media.split(';', 1)[0]
        return media in ALLOWED_MEDIA or (media.startswith('text/') and media not in DISALLOWED_MEDIA)
    elif not REQUIRE_MEDIA_TYPE:
        return is_allowed_extension(version['capture_url'])
    else:
        return False


class AnalyzableError(ValueError):
    ...


def assert_can_analyze(page):
    a = page['earliest']
    b = page['latest']
    if a['uuid'] == b['uuid']:
        raise AnalyzableError('Page has only one version')

    if not is_fetchable(a['uri']) or not is_fetchable(b['uri']):
        raise AnalyzableError('Raw response data for page is not retrievable')

    if not is_analyzable_media(a) or not is_analyzable_media(b):
        raise AnalyzableError('Media types of versions cannot be analyzed')

    return True


# Analysis! -------------------------------------------------------------------

def calculate_percent_changed(diff):
    total_size = 0
    changed_size = 0
    for operation, text in diff:
        total_size += len(text)
        if operation != 0:
            changed_size += len(text)

    if total_size == 0:
        return 0.0

    return changed_size / total_size


def analyze_page(page, grams):
    """
    Analyze a page from web-monitoring-db and return information about how the
    words on it changed between the first and latest captured versions.
    """
    assert_can_analyze(page)

    version_first = page['earliest']
    version_last = page['latest']

    response_a, response_b = parallel((load_url_readability, version_first['uri']),
                                      (load_url_readability, version_last['uri']))
    # load_url_text returns None if the content couldn't be parsed by
    # readability. If either one of the original documents couldn't be parsed,
    # fall back to straight HTML text for *both* (we want what we're diffing to
    # conceptually match up).
    if response_a and response_b:
        text_a = response_a.text
        text_b = response_b.text
        raw_diff = differs.html_source_diff(text_a, text_b)
    else:
        response_a, response_b = parallel((load_url, version_first['uri']),
                                          (load_url, version_last['uri']))
        text_a = re.sub(r'[\s\r\n]+', ' ', response_a.text)
        text_b = re.sub(r'[\s\r\n]+', ' ', response_b.text)
        raw_diff = differs.html_text_diff(text_a, text_b)

    # This script leverages our textual diffing routines, which work
    # character-by-character, so we have to recompose the results into *words*.
    # That's a little absurd, and we might be better off in the future to
    # tokenize the words and diff them directly instead.
    word_diff = CharacterToWordDiffs.word_diffs(raw_diff['diff'])

    # Count the terms that were added and removed.
    terms = (Counter(), Counter(),)
    for gram in range(1, grams + 1):
        terms[0].update(Counter(changed_ngrams(word_diff[0], gram)))
        terms[1].update(Counter(changed_ngrams(word_diff[1], gram)))

    return {
        'id': page['uuid'],
        'first_id': version_first['uuid'],
        'last_id': version_last['uuid'],
        'url': page['url'],
        'title': page['title'],
        'status': version_last['status'],
        'first_date': version_first['capture_time'].isoformat() + 'Z',
        'last_date': version_last['capture_time'].isoformat() + 'Z',
        'percent_changed': calculate_percent_changed(raw_diff['diff']),
        'terms': terms,
    }


def process_page(page, grams=2):
    """
    In-process wrapper for analyze_page() that handles exceptions because
    Python multiprocessing seems to have issues with actual raised exceptions.
    """
    try:
        analyzed = analyze_page(page, grams)
        # Percent changed can be > 0 even when no words changed if only
        # whitespace changed. Not ideal, but oh well.
        if analyzed['percent_changed'] > 0 and (len(analyzed['terms'][0]) > 0 or len(analyzed['terms'][1]) > 0):
            return analyzed
        else:
            return None
    except Exception as error:
        error.page_id = page['uuid']
        return error


def analyze_pages(pages, grams=2, parallel=10):
    """
    Analyze a set of pages in parallel across multiple processes. Yields the
    result of analyzing each page, which may be:
    - A dict (analysis result)
    - An exception
    - None (page could not be analyzed and was skipped)
    """
    with concurrent.futures.ProcessPoolExecutor(max_workers=parallel) as executor:
        analyses = (executor.submit(process_page, page, grams) for page in pages)
        for item in concurrent.futures.as_completed(analyses):
            yield item.result()


# Grabbing Data from the Web Monitoring Database ------------------------------

def get_page_count(url_pattern):
    client = db.Client.from_env()
    data = client.list_pages(chunk_size=1, url=url_pattern, active=True,
                             include_total=True)
    return data['meta']['total_results']


def list_all_pages(url_pattern):
    client = db.Client.from_env()
    chunk = 1
    while chunk > 0:
        pages = request_page_chunk(client, url_pattern, chunk)
        yield from pages['data']
        chunk = pages['links']['next'] and (chunk + 1) or -1


def request_page_chunk(client, url_pattern, chunk=1, retries=2):
    try:
        return client.list_pages(sort=['created_at:asc'], chunk_size=1000,
                                 chunk=chunk, url=url_pattern, active=True,
                                 include_earliest=True, include_latest=True)
    except Exception:
        if retries > 0:
            return request_page_chunk(url_pattern, chunk, retries - 1)
        else:
            raise


# Output and Main Program -----------------------------------------------------

def write_page_to_stdout(page):
    print(json.dumps(page, separators=(',', ':')))


def message(text):
    """
    Log a user-facing message to stderr (we print program output on stdout so
    you can pipe it to a file, so informational messages go on stderr).
    """
    print(text, file=sys.stderr)


@contextmanager
def cached_requests(enable, *args, **kwargs):
    """
    Cache HTTP requests made inside this context manager in a file at
    `./cache.sqlite`.
    """
    if enable:
        # Monkey patch requests with a cache :D
        import requests_cache
        requests_cache.install_cache(backend='sqlite', expire_after=24*60*60)

    yield

    if enable:
        requests_cache.uninstall_cache()


def main(pattern=None, grams=2, sqlite_path=None, cache=False, verbose=False):
    # Only cache this part -- the actual analysis work is multiprocess, and
    # will probably have major locking issues with the cache file :(
    with cached_requests(cache):
        # Get metadata about pages and versions from web-monitoring-db
        total = get_page_count(pattern)
        pages = list(tqdm(list_all_pages(pattern), desc='loading metadata', unit=' pages'))

    with sqlite_database(sqlite_path) as database:
        unchanged = 0
        skipped = []
        failed = []

        # Actually analyze the pages and output the results.
        for result in tqdm(analyze_pages(pages, grams), desc='analyzing', unit=' pages', total=total):
            if isinstance(result, AnalyzableError):
                skipped.append(result)
            elif isinstance(result, Exception):
                failed.append(result)
            elif result:
                write_page_to_stdout(result)
                write_page_to_sqlite(result, database, KEY_TERMS)
            else:
                unchanged += 1

        if unchanged > 0:
            message(f'{unchanged} pages had no textual changes.')

        if len(skipped) > 0:
            message(f'{len(skipped)} pages could not be analyzed.')
            if verbose:
                for page in skipped:
                    message(f'  {page.page_id} ({page})')

        if len(failed) > 0:
            message(f'Failed to analyze {len(failed)} pages.')
            if verbose:
                for page in failed:
                    message(f'  {page.page_id} ({page})')
