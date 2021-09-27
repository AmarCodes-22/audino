import argparse
import os
from pprint import pprint
import sys

from bs4 import BeautifulSoup
import requests
import yaml

from pkgs.utils import config_system

# load the configs into respective dicts
paths_dict = config_system.load_paths_config()
books_dict = config_system.load_books_config(paths_dict['books_config_file'])
audio_dict = config_system.load_audio_config(paths_dict['audio_config_file'])
summary_dict = config_system.load_summary_config(paths_dict['summary_config_file'])

# base url for the book webpage on project gutenberg
BASE_URL = 'https://www.gutenberg.org/ebooks/'

def store_webpage_content(book_id, html_content_file_path):
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
    with open(html_content_file_path, 'w') as file:
        file.write(str(webpage_html))

def get_epub_and_raw(html_path, epub_file_path, raw_file_path):
    """
    Get the epub and raw text format and store them
    Args:
        html_path (str): path to the html content for the current book_id
        epub_file_path (str): path to store the epub file
        raw_file_path (str): path to store the raw file
    Returns:
        None
    """
    with open(html_path) as file:
        soup = BeautifulSoup(file, 'html.parser')
        # print(soup.prettify())

def get_thumbnail(html_path, thumbnail_path):
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
        command = f'wget -O {thumbnail_path} {image_link}'
        os.system(command)

def setup_book(book_id):
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
    get_epub_and_raw(book_id_html, book_id_epub_file, book_id_raw_file)

    # getting the thumbnail
    if not os.path.exists(book_id_thumbnail):
        get_thumbnail(book_id, book_id_html, book_id_thumbnail)
    else:
        print("Thumbnail already exists, not downloading again, don't wanna get IP blocked")
    files_dict['thumbnail'] = book_id_thumbnail

def main():
    parser = argparse.ArgumentParser(description='try to print out the book id')
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

"""todo
    > add a function to download the epub and raw text and put it inside data/book_id/ 
        > book_id 84
    > add a function to get the thumbnail 
    > add a function to get the genre
    > add a function to add the book to the books.yml file

"""