import argparse
import os
from pprint import pprint
import subprocess

from bs4 import BeautifulSoup
from nltk import FreqDist
import requests
from nltk.tokenize import word_tokenize

from pkgs.utils import config_system

# import nltk
# punkt download (one time only)
# nltk.download('punkt')


class Book():
    def __init__(self,
                 paths: dict, files_dict: dict, meta_dict: dict, book_id: str):
        """Initializes a book object

        Args:
            paths (dict): paths to common directories in the project
            files_dict (dict): empty dictionary which will contain file paths
                for the current book
            meta_dict (dict): empty dictionary which will contain meta data
            book_id (str): book_id of the book
        """
        self.book_id = book_id
        self.BASE_EBOOK_URL = 'https://www.gutenberg.org/ebooks/'

        # populate paths for local files
        self.dir_path = os.path.join(paths['data_dir'], book_id)
        self.html_fpath = os.path.join(self.dir_path, book_id + '.html')
        self.thumbnail_fpath = os.path.join(self.dir_path, book_id + '.jpg')
        self.epub_fpath = os.path.join(self.dir_path, book_id + '.epub')
        self.raw_fpath = os.path.join(self.dir_path, book_id + '.txt')

        self.files_dict = files_dict
        self.meta_dict = meta_dict
        print(f'Book id: {self.book_id}')

    def store_html_file(self):
        """Gets the HTML file from web and stores it locally
        """
        # check if the html file already exists
        if os.path.exists(self.html_fpath):
            print(f'Html file already saved: {self.html_fpath}')
            self.files_dict['html'] = self.html_fpath

        else:
            # getting the webpage html
            res = requests.get(self.BASE_EBOOK_URL + self.book_id)
            webpage_html = str(BeautifulSoup(res.content, 'html.parser'))

            # make directories if they don't exist
            os.makedirs(os.path.dirname(self.html_fpath), exist_ok=True)

            # storing the webpage content in a file
            print('\n\n-----Storing html-----\n\n')
            with open(self.html_fpath, 'w') as file:
                file.write(webpage_html)

            # populating files dictionary
            self.files_dict['html'] = self.html_fpath
            print(f'HTML file stored at: {self.html_fpath}')

    def store_epub(self):
        """Gets the EPUB format from web and stores it locally
        """
        # check if the EPUB file already exists
        if os.path.exists(self.epub_fpath):
            print(f'Epub file already saved: {self.epub_fpath}')
            self.files_dict['epub'] = self.epub_fpath
        else:
            BASE_URL = 'https://www.gutenberg.org'
            epub_url = None
            download, link, epub = False, False, False
            with open(self.html_fpath) as file:
                soup = BeautifulSoup(file, 'html.parser')

                # distinguish the EPUB url
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
                print('\n\n-----Saving epub-----\n\n')
                command = f'wget -O {self.epub_fpath} {epub_url}'

                # using shell=True does not give FileNotFound error in wget
                subprocess.run(command, shell=True)
                # os.system(command)
                self.files_dict['epub'] = self.epub_fpath
                print(f'Epub file stored at: {self.epub_fpath}')

    def store_raw(self):
        """Gets the raw text format from web and save it
        """
        # check if the raw file already exists
        if os.path.exists(self.raw_fpath):
            print(f'Raw file already saved: {self.raw_fpath}')
            self.files_dict['raw'] = self.raw_fpath
        else:
            # # make directories if they don't exist
            # os.makedirs(os.path.dirname(self.html_fpath), exist_ok=True)

            BASE_URL = 'https://www.gutenberg.org'
            raw_url = None
            download, link, raw = False, False, False
            with open(self.html_fpath) as file:
                soup = BeautifulSoup(file, 'html.parser')

                # distinguish raw text file url
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
                print('\n\n-----Saving raw-----\n\n')
                command = f'wget -O {self.raw_fpath} {raw_url}'
                subprocess.run(command, shell=True)
                # os.system(command)
                self.files_dict['raw'] = self.raw_fpath
                print(f'Raw file stored at: {self.raw_fpath}')

    def store_thumbnail(self):
        """Get the thumbnail for the book
        """
        # check if the thumbnail file already exists
        if os.path.exists(self.thumbnail_fpath):
            print(f'Thumbnail already saved: {self.thumbnail_fpath}')
            self.files_dict['thumbnail'] = self.thumbnail_fpath
        else:
            with open(self.html_fpath) as file:
                soup = BeautifulSoup(file, 'html.parser')
                image_url = None

                # find the thumbnail url
                for image in soup.find_all('img'):
                    if image.get('title') == 'Book Cover':
                        image_url = image.get('src')

                # saving the file
                if image_url:
                    print('\n\n-----Saving thumbnail-----\n\n')
                    command = f'wget -O {self.thumbnail_fpath} {image_url}'
                    subprocess.run(command, shell=True)
                    # os.system(command)
                    self.files_dict['thumbnail'] = self.thumbnail_fpath
                    print(f'Thumbnail stored at: {self.thumbnail_fpath}')

    def get_genre(self):
        """Get the genre of the book
        """
        subjects = list()

        # Getting the subjects
        with open(self.html_fpath) as file:
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

        # Getting the most frequent subjects to be used as tags
        subjects_str = ' '.join(subjects)
        subjects_tokenized = word_tokenize(subjects_str)
        fdist = FreqDist(subjects_tokenized)
        genre = fdist.most_common(1)[0][0]
        self.meta_dict['genreName'] = genre

    def get_book_config(self):
        """Returns the files, meta_data dictionary

        Returns:
            [tuple]: [files_dict, meta_dict]
        """
        return self.files_dict, self.meta_dict


def setup_book(book_id: str):
    """Makes a new directory for the book and populates files

    Args:
        book_id (str): ID of the current book as provided by ProjectGutenberg
    """

    # Load the configs
    paths_dict = config_system.load_paths_config()

    # Initialize the dicts
    files_dict = dict()
    meta_dict = dict()

    # initialize the book and get the data
    book = Book(paths_dict, files_dict, meta_dict, book_id)
    book.store_html_file()
    book.store_raw()
    book.store_epub()
    book.store_thumbnail()
    book.get_genre()

    # dictionaries to populate and store in the yml file at the end
    files_dict, meta_dict = book.get_book_config()

    # initialize the rest of keys in files dict
    files_dict['audio'] = None
    files_dict['summary_json'] = None
    files_dict['summary_text'] = None
    pprint(files_dict)

    # initialize rest of meta_data
    meta_dict['bookName'] = None
    meta_dict['authorName'] = None
    meta_dict['thumbnailUrl'] = None
    meta_dict['Description'] = None
    # meta_dict['SummaryText'] = None
    meta_dict['audioUrl'] = None
    pprint(meta_dict)

    # joining the two dictionaries for the final dictionary
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
