import argparse
import os
from pprint import pprint

from bs4 import BeautifulSoup
from nltk import FreqDist
import requests
from nltk.tokenize import word_tokenize
from requests.api import head

from pkgs.utils import config_system

# punkt download (one time only)
# nltk.download('punkt')

class Book():
    def __init__(self, paths:dict, files_dict:dict, meta_dict:dict, book_id:str):
        self.book_id = book_id
        self.dir = os.path.join(paths['data_dir'], book_id)
        self.BASE_EBOOK_URL = 'https://www.gutenberg.org/ebooks/'
        self.html_file_path = os.path.join(self.dir, book_id + '.html')
        self.thumbnail_file_path = os.path.join(self.dir, book_id + '.jpg')
        self.epub_file_path = os.path.join(self.dir, book_id + '.epub')
        self.raw_file_path = os.path.join(self.dir, book_id + '.txt')
        self.files_dict = files_dict
        self.meta_dict = meta_dict
        print(f'Book id: {self.book_id}')

    def store_html_file(self):
        """ Get the webpage html and store it in a file """
        if os.path.exists(self.html_file_path):
            print(f'Html file already saved: {self.html_file_path}')
            self.files_dict['html'] = self.html_file_path
            
        else:
            # getting the webpage html
            res = requests.get(self.BASE_EBOOK_URL + self.book_id)
            webpage_html = BeautifulSoup(res.content, 'html.parser')

            # make directories if they don't exist
            os.makedirs(os.path.dirname(self.html_file_path), exist_ok=True)

            # storing the webpage content in a file
            print('Storing html')
            with open(self.html_file_path, 'w') as file:
                file.write(str(webpage_html))
            self.files_dict['html'] = self.html_file_path
            print(f'HTML file stored at: {self.html_file_path}')

    def store_epub(self):
        """ Get the epub text format and store it """
        if os.path.exists(self.epub_file_path):
            print(f'Epub file already saved: {self.epub_file_path}')
            self.files_dict['epub'] = self.epub_file_path
        else:
            BASE_URL = 'https://www.gutenberg.org'
            epub_url = None
            download, link, epub = False, False, False
            with open(self.html_file_path) as file:
                soup = BeautifulSoup(file, 'html.parser')
                for a in soup.find_all('a'):
                    if a.get('title'):
                        if 'Download' in a.get('title'):
                            download = True
                    if a.get('class'):
                        if 'link' in a.get('class'):
                            link = True
                    if a.text:
                        if 'EPUB (no images)' in a.text:
                            epub = True
                    if download and link and epub:
                        print(a)
                        epub_url = BASE_URL + a['href']
                        break

            if epub_url:
                print('Saving epub')
                command = f'wget -O {self.epub_file_path} {epub_url}'
                os.system(command)
                self.files_dict['epub'] = self.epub_file_path
                print(f'Epub file stored at: {self.epub_file_path}')

    def store_raw(self):
        """ Get the raw text format and save it """
        if os.path.exists(self.raw_file_path):
            print(f'Raw file already saved: {self.raw_file_path}')
            self.files_dict['raw'] = self.raw_file_path
        else:
            BASE_URL = 'https://www.gutenberg.org'
            raw_url = None
            download, link, raw = False, False, False
            with open(self.html_file_path) as file:
                soup = BeautifulSoup(file, 'html.parser')
                for a in soup.find_all('a'):
                    if a.get('title'):
                        if 'Download' in a.get('title'):
                            download = True
                    if a.get('class'):
                        if 'link' in a.get('class'):
                            link = True
                    if a.text:
                        if 'Plain Text' in a.text:
                            raw = True
                    if download and link and raw:
                        raw_url = BASE_URL + a['href']
                        break

            if raw_url:
                print('Saving epub')
                command = f'wget -O {self.raw_file_path} {raw_url}'
                os.system(command)
                self.files_dict['raw'] = self.raw_file_path
                print(f'Raw file stored at: {self.raw_file_path}')

    def store_thumbnail(self):
        """ Get the thumbnail for the book """
        if os.path.exists(self.thumbnail_file_path):
            print(f'Thumbnail already saved: {self.thumbnail_file_path}')
            self.files_dict['thumbnail'] = self.thumbnail_file_path
        else:
            with open(self.html_file_path) as file:
                soup = BeautifulSoup(file, 'html.parser')
                image_url = None

                # finding the thumbnail url
                for image in soup.find_all('img'):
                    if image.get('title') == 'Book Cover':
                        image_url = image.get('src')

                # saving the file
                if image_url:
                    print('Saving thumbnail')
                    command = f'wget -O {self.thumbnail_file_path} {image_url}'
                    os.system(command)
                    self.files_dict['thumbnail'] = self.thumbnail_file_path
                    print(f'Thumbnail stored at: {self.thumbnail_file_path}')

    def get_genre(self):
        """ Get the genre """
        subjects = list()
        # Getting the subjects
        with open(self.html_file_path) as file:
            soup = BeautifulSoup(file, 'html.parser')
            table_rows = soup.find_all('tr')
            for row in table_rows:
                headers = row.findChildren(['th'])
                for header in headers:
                    if header.text == 'Subject':
                        curr_subject = row.td.text
                        for char in ['\n', '-']:
                            curr_subject = curr_subject.replace(char, '')
                        curr_subject.strip().lower()
                        subjects.append(curr_subject)

        # Getting the most common subjects to be used as tags
        subjects_str = ' '.join(subjects)
        subjects_tokenized = word_tokenize(subjects_str)
        fdist = FreqDist(subjects_tokenized)
        genre = fdist.most_common(1)[0][0]
        self.meta_dict['Genre'] = genre

    def get_book_config(self):
        return self.files_dict, self.meta_dict

def setup_book(book_id:str):
    """Makes a new directory for the new book and sets up the file paths"""

    # Load the configs 
    paths_dict = config_system.load_paths_config()

    # Initialize the dicts
    files_dict = dict()
    meta_dict = dict()

    book = Book(paths_dict, files_dict, meta_dict, book_id)
    book.store_html_file()
    book.store_raw()
    book.store_epub()
    book.store_thumbnail()
    book.get_genre()

    # dictionaries to populate and store in the yml file at the end
    files_dict, meta_dict = book.get_book_config()

    # initialize the files dict
    files_dict['audio'] = None
    files_dict['summary_json'] = None
    files_dict['summary_text'] = None
    pprint(files_dict)

    meta_dict['Title'] = None 
    meta_dict['Author'] = None 
    meta_dict['ThumbnailUrl'] = None 
    meta_dict['Description'] = None 
    meta_dict['SummaryUrl'] = None 
    meta_dict['AudioUrl'] = None
    pprint(meta_dict)

    final_dict = {
        book_id: {
            'files': files_dict,
            'meta': meta_dict
        }
    }

    config_system.update_books(final_dict)

def main():
    parser = argparse.ArgumentParser(
        description='Add new book data to the books.yml file'
    )
    parser.add_argument(
        '--bookid',
        dest='book_id',
        type=str, 
        help='enter the book id', 
        required=True
    )
    args = parser.parse_args()
    setup_book(book_id=args.book_id)

if __name__ == '__main__':
    main()
