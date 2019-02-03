import json
from os import path
from time import sleep

from bs4 import BeautifulSoup
import requests

import constants
from exceptions import NoDataException


class LitEraParser(object):
    """Простой парсер книг с сайта lit-era. Создан в учебных целях.

    .. usage::

        LitEraParser(book_slug).parse_to_file(book_file_name)

    """

    csrf_token = ''

    def __init__(self, book_slug):
        self.book_url = path.join(constants.LITERA_BOOKS_URL, book_slug)
        self._session = None
        self._chapter_id_list = None
        self._init_book()

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                'user-agent': 'Browser 2.1',
                'accept-language': 'en-US, en; q = 0.8',
                'x-requested-with': 'XMLHttpRequest'
            })
        return self._session

    def _init_book(self):

        html_response = self.session.get(self.book_url)
        html_parser = BeautifulSoup(html_response.text, 'html.parser')

        chapters = html_parser.find('select', {'name': 'chapter'})
        self._chapter_id_list = [
            option_element.attrs['value']
            for option_element in chapters.find_all('option')
        ]

        token_meta = html_parser.find('meta', {'name': 'csrf-token'})
        self.csrf_token = token_meta.attrs['content']

        self.session.headers.update({
            'origin': constants.LITERA_ORIGIN_URL,
            'referer': self.book_url,
            'x-csrf-token': self.csrf_token
        })

    def _get_page(self, chapter_id, page):

        post_params = {
            'chapterId': chapter_id,
            'page': page,
            '_csrf': self.csrf_token
        }

        response_data = self.session.post(
            constants.LITERA_GET_PAGE_URL, post_params
        )
        response_json = json.loads(response_data.text)

        if not response_json['status']:
            raise NoDataException(response_json['data'])

        page_parser = BeautifulSoup(response_json['data'], 'html.parser')

        # Filter from so-called "protection" tags
        for bad_span in page_parser.find_all('span'):
            bad_span.replace_with('')
        [x.extract() for x in page_parser.findAll('i')]

        return page_parser.text, response_json['isLastPage']

    def _get_chapter(self, chapter_id):

        self.session.headers['referer'] = '{}?c={}'.format(
            self.book_url, chapter_id
        )

        total_chapter_text = ''

        try:
            for page in range(1, constants.MAX_PAGES_PER_CHAPTER):
                chapter_text, is_last_page = self._get_page(chapter_id, page)
                total_chapter_text += chapter_text
                if is_last_page:
                    break
                sleep(constants.WAIT_BETWEEN)
        except NoDataException as ex:
            print('Error! ', ex)

        total_chapter_text += '\n\n'

        return total_chapter_text

    def parse_to_file(self, book_file_name):
        with open(book_file_name, 'w') as text_file:
            print('Progress: ', end="")
            for index, chapter_id in enumerate(self._chapter_id_list):
                progress = int(index * 100 / len(self._chapter_id_list))
                print(progress, end="..", flush=True)
                text_file.write(self._get_chapter(chapter_id))
            print('100..OK')
