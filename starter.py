#! /usr/bin/python3

import argparse

from parser import LitEraParser


def main(book_slug, book_file_name, login, password):
    credentials = None
    if login and password:
        credentials = (login, password)

    LitEraParser(book_slug, credentials).parse_to_file(book_file_name)


if __name__ == '__main__':

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        '-s', '--slug', required=True,
        help='Book slug from browser, example: "volchya-tropa-b34046".'
    )
    argument_parser.add_argument(
        '-o', '--output', required=True,
        help='File name to save book.'
    )
    argument_parser.add_argument(
        '-l', '--login', required=False, help='Your login.', default=''
    )
    argument_parser.add_argument(
        '-p', '--password', required=False, help='Your password.', default=''
    )
    arguments = argument_parser.parse_args()

    main(arguments.slug, arguments.output, arguments.login, arguments.password)
