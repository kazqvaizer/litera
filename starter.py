#! /usr/bin/python3

import argparse

from parser import LitEraParser


def main(book_slug, book_file_name):

    LitEraParser(book_slug).parse_to_file(book_file_name)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--slug', required=True,
        help='Book slug from browser, example: "volchya-tropa-b34046".'
    )
    parser.add_argument(
        '-o', '--output', required=True,
        help='File name to save book.'
    )
    parsed = parser.parse_args()

    main(parsed.slug, parsed.output)
