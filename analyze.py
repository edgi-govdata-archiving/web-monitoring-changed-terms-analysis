from changed_terms_analysis.analyze import main
import sys

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Count term changes in monitored pages.')
    parser.add_argument('--pattern', help='Only analyze pages with URLs matching this pattern.')
    parser.add_argument('--ngrams', type=int, default=2, help='Number of words in combination to track.')
    parser.add_argument('--sqlite', help='Output results in a sqlite DB at this path.')
    parser.add_argument('--cache', action='store_true', help='Cache HTTP requests')
    parser.add_argument('--verbose', action='store_true', help='Show details about skips and errors')
    # Need the ability to actually start/stop the readability server if we want this option
    # parser.add_argument('--readability', action='store_true', help='Only analyze pages with URLs matching this pattern.')
    options = parser.parse_args()

    if options.ngrams < 1 or options.ngrams > 5:
        print('--ngrams must be between 1 and 5.', file=sys.stderr)
        sys.exit(1)

    main(pattern=options.pattern,
         grams=options.ngrams,
         sqlite_path=options.sqlite,
         cache=options.cache,
         verbose=options.verbose)
