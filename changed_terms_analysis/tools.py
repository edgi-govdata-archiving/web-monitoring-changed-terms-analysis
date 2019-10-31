from collections import Counter
import concurrent.futures
from nltk.corpus import stopwords
import re
import requests
from retry import retry


BOUNDARY = re.compile(r'[\r\n\s.;:!?,<>{}[\]\-–—\|\\/]+')
IGNORABLE = re.compile('[\'‘’"“”]')
STOPWORDS = set(map(lambda word: IGNORABLE.sub('', word),
                    stopwords.words('english')))
STOPWORDS.add('&')


class CharacterToWordDiffs:
    """
    Convert a character-by-character diff to a word-by-word diff. Resulting
    words are normalized -- they are all lowercase, punctuation is removed,
    etc. The tokenization here is also a little naive.
    """

    @classmethod
    def word_diffs(cls, text_changes):
        insertions = CharacterToWordDiffs(1)
        deletions = CharacterToWordDiffs(-1)

        for change in text_changes:
            if change[0] == 0 or change[0] == 1:
                insertions.add_text(change[1], change[0] != 0)

            if change[0] == 0 or change[0] == -1:
                deletions.add_text(change[1], change[0] != 0)

        insertions.add_text('', False)
        deletions.add_text('', False)

        return deletions.diff, insertions.diff

    def __init__(self, change_type):
        self.diff = []
        self.buffer = ''
        self.has_change = False
        self.change_type = change_type

    def add_text(self, text, is_change):
        remaining = text
        remaining = IGNORABLE.sub('', remaining)
        while True:
            boundary = BOUNDARY.search(remaining)
            if boundary is None:
                break

            if boundary.start() > 0:
                self.has_change = is_change or self.has_change
                self.buffer += remaining[:boundary.start()]
            self.complete_word()
            remaining = remaining[boundary.end():]

        if remaining:
            self.has_change = is_change or self.has_change
            self.buffer += remaining

        if text == '':
            self.complete_word()

    def complete_word(self):
        # TODO: get the stem instead of the word?
        # TODO: recognize `. ` as a sentence break and use it when n-gramming
        #       Probably similar things like em dashes, semicolons, commas
        word = self.buffer.lower()
        change_type = self.change_type if self.has_change else 0
        if word:
            self.diff.append((change_type, word))

        self.has_change = False
        self.buffer = ''


def changed_ngrams(diff, size=1):
    token_buffer = []
    change_buffer = []
    for item in diff:
        if item[1] in STOPWORDS:
            token_buffer.clear()
            change_buffer.clear()
        else:
            token_buffer.append(item[1])
            change_buffer.append(item[0])
            if len(token_buffer) == size:
                if any(change_buffer):
                    yield ' '.join(token_buffer)
                token_buffer.pop(0)
                change_buffer.pop(0)


def net_change(deletions, additions):
    """
    Helper for figuring out the overall change in usage of a set of terms.
    """
    net_count = Counter(additions)
    net_count.subtract(Counter(deletions))
    zeros = [key for key, value in net_count.items() if value == 0]
    for key in zeros:
        del net_count[key]

    return net_count


@retry(tries=3, delay=1)
def load_url(url, **request_args):
    response = requests.get(url, timeout=15, **request_args)
    if not response.ok:
        response.raise_for_status()

    content_type = response.headers.get('content-type', '')
    if 'charset=' not in content_type:
        response.encoding = 'utf-8'

    return response


@retry(tries=3, delay=1)
def load_url_readability(url):
    response = load_url(f'http://localhost:7323/proxy', params={'url': url})

    # Return None if the URL was unparseable.
    if response.status_code >= 400:
        return None
    else:
        return response


def parallel(*calls):
    """Run several function calls in parallel threads."""
    calls = list(calls)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(calls)) as executor:
        tasks = [executor.submit(call, *args) for call, *args in calls]
        return [task.result() for task in tasks]
