
import json
from os import path

from bs4 import BeautifulSoup
import requests

from exceptions import NoDataException


MAX_PAGES_PER_CHAPTER = 10000


class LitEraParser(object):

    csrf_token = ''
    chapter_id_list = []
    _session = None

    def __init__(self, book_slug):
        self.book_url = path.join(LITERA_BOOKS_URL, book_slug)

    @property
    def session(self):

        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                'user-agent': (
                    'Browser 2.0'
                )
            })
            self._init_book()

        return self._session

    def _init_book(self):

        html_response = self.session.get(self.book_url)
        html_parser = BeautifulSoup(html_response.content, 'html.parser')

        chapters = html_parser.find('select', {'name': 'chapter'})
        self.chapter_id_list = [
            option_element.attrs['value']
            for option_element in chapters.find_all('option')
        ]

        token_meta = html_parser.find('meta', {'name': 'csrf-token'})
        self.csrf_token = token_meta.attrs['content']

        self.session.headers.update({
            'origin': LITERA_ORIGIN_URL,
            'referer': self.book_url,
            'accept': 'application/json, text/javascript, */*; q = 0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US, en; q = 0.8',
            'content-length': '90',
            'x-csrf-token': self.csrf_token,
            'x-requested-with': 'XMLHttpRequest'
        })

    def _get_page(self, chapter_id, page):

        post_params = {
            'chapterId': chapter_id,
            'page': page,
            '_csrf': self.csrf_token
        }

        response_data = self.session.post(LITERA_GET_PAGE_URL, post_params)
        response_json = json.loads(response_data.text)

        if not response_json['status']:
            raise NoDataException(response_json['data'])

        page_parser = BeautifulSoup(response_json['data'], 'html.parser')

        for bad_span in page_parser.find_all('span'):
            bad_span.replace_with('')

        return page_parser.text, response_json['isLastPage']

    def get_chapter(self, chapter_id):

        self.session.headers['referer'] = '{}?c={}'.format(
            self.book_url, chapter_id
        )

        total_chapter_text = ''

        try:
            for page in range(1, MAX_PAGES_PER_CHAPTER):
                chapter_text, is_last_page = self._get_page(chapter_id, page)
                total_chapter_text += chapter_text
                if is_last_page:
                    break
        except NoDataException as ex:
            print('Error! ', ex)

        total_chapter_text += '\n\n'

        return total_chapter_text


book_slug = 'volchya-tropa-b34046'

book_file_name = path.join(BOOK_OUT_DIR, book_slug + '.txt')

parser = LitEraParser(book_slug)
with open(book_file_name, 'w') as text_file:
    print('Progress: ', end="")
    for index, chapter_id in enumerate(parser.chapter_id_list):
        progress = int(index * 100 / len(parser.chapter_id_list))
        print(progress, end="..", flush=True)
        text_file.write(parser.get_chapter(chapter_id))
    print('100..OK')
