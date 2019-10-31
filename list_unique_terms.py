from collections import Counter
import csv
import json
import re
import sys


def json_lines(filepath):
    with open(filepath) as file:
        for line in file:
            if line.strip():
                yield json.loads(line)


SKIPPABLE_TERM = re.compile(r'(^[!@#$%^&*()<>,./?"=\-]*$)|(^\d*(\.\d*)?$)')


def filter_term(term, length=0):
    return len(term) > length and SKIPPABLE_TERM.search(term) is None


def filter_terms(counter, min_count=5, min_length=2):
    return {term: count
            for term, count in counter.items()
            if count > min_count and filter_term(term, length=min_length)}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='List all unique terms in an analysis’s JSON output as a CSV.')
    parser.add_argument('PATH', help='Path to analysis JSON output file.')
    parser.add_argument('--sort', help='Sort by `count` or `term`.', default='term')
    parser.add_argument('--count', type=int, help='Only include terms that changed on at least this many pages.', default=1)
    parser.add_argument('--length', type=int, help='Only include terms that with at least this many characters.', default=2)
    options = parser.parse_args()

    terms_and_pages = Counter()
    for page_data in json_lines(options.PATH):
        terms = page_data['terms']
        all_terms = set(terms[0].keys()).union(set(terms[1].keys()))
        terms_and_pages.update({term: 1 for term in all_terms})

    results = sorted(filter_terms(terms_and_pages,
                                  min_count=options.count,
                                  min_length=options.length).items(),
                     key=lambda x: options.sort == 'term' and x[0] or x[1],
                     reverse=(options.sort == 'count'))

    writer = csv.writer(sys.stdout)
    writer.writerow(['term', 'page_count'])
    for term, page_count in results:
        writer.writerow([term, page_count])
