import argparse
import os
from pprint import pprint
import sys

from bs4 import BeautifulSoup
from nltk import FreqDist
import nltk
import requests
from nltk.tokenize import word_tokenize
import yaml

from pkgs.utils import config_system

# punkt download (one time download)
# nltk.download('punkt')

# load the configs into respective dicts
paths_dict = config_system.load_paths_config()
books_dict = config_system.load_books_config(paths_dict['books_config_file'])
audio_dict = config_system.load_audio_config(paths_dict['audio_config_file'])
summary_dict = config_system.load_summary_config(paths_dict['summary_config_file'])

# base url for the book webpage on project gutenberg
BASE_URL = 'https://www.gutenberg.org/ebooks/'

def store_webpage_content(book_id:str, html_content_file_path:str):
    """
    Get the webpage html and store it in a file
    Args:
        book_id (str): unique id used to get the html
        html_content_file_path (str): path to store the html file in
    Returns:
        None
    """
    # getting the webpage html
    res = requests.get(BASE_URL + book_id)
    webpage_html = BeautifulSoup(res.content, 'html.parser')

    # make directories if they don't exist
    os.makedirs(os.path.dirname(html_content_file_path), exist_ok=True)

    # storing the webpage content in a file
    print('Storing html')
    with open(html_content_file_path, 'w') as file:
        file.write(str(webpage_html))

def get_epub_and_raw(html_path:str, epub_file_path:str, raw_file_path:str):
    """
    Get the epub and raw text format and store them
    Args:
        html_path (str): path to the html content for the current book_id
        epub_file_path (str): path to store the epub file
        raw_file_path (str): path to store the raw file
    Returns:
        None
    """
    BASE_EPUB_RAW_URL = 'https://www.gutenberg.org'
    epub_url, raw_url = None, None

    # parsing to find the epub url
    with open(html_path) as file:
        soup = BeautifulSoup(file, 'html.parser')
        download, link, epub = False, False, False
        href = None
        for a in soup.find_all('a'):
            # print(a.get('title'), a.get('class'), a.text)
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
                epub_url = BASE_EPUB_RAW_URL + a['href']
                break

    if epub_url:
        print('Saving epub')
        command = f'wget -O {epub_file_path} {epub_url}'
        os.system(command)

    # parsing to find the raw url
    with open(html_path) as file:
        soup = BeautifulSoup(file, 'html.parser')
        download, link, raw = False, False, False
        href = None
        for a in soup.find_all('a'):
            # print(a.get('title'), a.get('class'), a.text)
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
                raw_url = BASE_EPUB_RAW_URL + a['href']
                break

    if raw_url:
        print('Saving raw')
        command = f'wget -O {raw_file_path} {raw_url}'
        os.system(command)

    # print(epub_url, raw_url)

def get_thumbnail(html_path:str, thumbnail_path:str):
    """
    Get the thumbnail for the book
    Args:
        html_path (str): path to html content for the current book_id
        thumbnail_path (str): path to store the thumbnail
    Returns:
        None
    """
    with open(html_path) as file:
        soup = BeautifulSoup(file, 'html.parser')
        image_link = None

        # find the thumbnail url
        for image in soup.find_all('img'):
            if image.get('title') == 'Book Cover':
                image_link = image.get('src')

        # saving the file 
        print('Saving thumbnail')
        command = f'wget -O {thumbnail_path} {image_link}'
        os.system(command)

def get_genre(html_path:str):
    """
    Get the genre 
    Args:
        html_path (str): path to the html page for the current book
    Returns:
        genre (str): predicted genre for the book
    """
    subjects = list()

    # Getting the subjects
    with open(html_path) as file:
        soup = BeautifulSoup(file, 'html.parser')
        table_rows = soup.find_all('tr')
        for row in table_rows:
            headers = row.findChildren(['th'])
            for header in headers:
                if header.text == 'Subject':
                    curr_subject = row.td.text
                    curr_subject = curr_subject.replace('\n', '').replace('-', '').strip().lower()
                    subjects.append(curr_subject)

    # Getting the most common subjects to be used as tags to determine the genre
    subjects_str = ' '.join(subjects)
    subjects_tokenized = word_tokenize(subjects_str)
    fdist = FreqDist(subjects_tokenized)
    genre = fdist.most_common(1)[0][0]
    return genre

def setup_book(book_id:str):
    """Makes a new directory for the new book and sets up the file paths"""
    # dictionaries to populate and store in the yml file at the end
    files_dict = dict()
    meta_data_dict = dict()

    # Sets up the book_id directory and the file paths 
    book_id_dir = os.path.join(paths_dict['data_dir'], book_id)
    book_id_epub_file = os.path.join(book_id_dir, book_id + '.epub')
    book_id_raw_file = os.path.join(book_id_dir, book_id + '.txt')
    book_id_thumbnail = os.path.join(book_id_dir, book_id + '.jpg')
    book_id_html = os.path.join(book_id_dir, book_id + '.html')

    # getting the html content
    if not os.path.exists(book_id_html):
        store_webpage_content(book_id, book_id_html)
    else:
        print("Html file already downloaded, not downloading again, don't wanna get IP blocked")

    # getting the epub and raw text format 
    if not os.path.exists(book_id_epub_file):
        get_epub_and_raw(book_id_html, book_id_epub_file, book_id_raw_file)
    else:
        print("raw and epub already downloaded, not downloading again, don't wanna get IP blocked")
    files_dict['epub'] = book_id_epub_file
    files_dict['raw'] = book_id_raw_file

    # getting the thumbnail
    if not os.path.exists(book_id_thumbnail):
        get_thumbnail(book_id_html, book_id_thumbnail)
    else:
        print("Thumbnail already exists, not downloading again, don't wanna get IP blocked")
    files_dict['thumbnail'] = book_id_thumbnail

    # Getting the genre
    genre = get_genre(book_id_html)
    files_dict['genre'] = genre

    # Initializing the meta data dict
    meta_data_dict['Title'] = None 
    meta_data_dict['Author'] = None 
    meta_data_dict['ThumbnailUrl'] = None 
    meta_data_dict['Genre'] = None 
    meta_data_dict['Description'] = None 
    meta_data_dict['SummaryUrl'] = None 
    meta_data_dict['AudioUrl'] = None

    # pprint(files_dict)
    # pprint(meta_data_dict)

    final_dict = {
        book_id: {
            'files': files_dict,
            'meta_data': meta_data_dict
        }
    }

    config_system.add_new_book(final_dict)

def main():
    parser = argparse.ArgumentParser(description='setup the books.yml config for the bookid provided')
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
