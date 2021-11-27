import argparse
import json
import os
# from pprint import pprint
from typing import Tuple

import ebooklib
from ebooklib import epub
from gensim import summarization

from pkgs.utils import config_system

# load paths, books dictionaries
paths_dict = config_system.load_paths_config()
books_dict = config_system.load_books_config(paths_dict['books_config_file'])
# pprint(books_dict)


def store_title_author(book: ebooklib.epub.EpubBook, book_id: str) -> None:
    """Stores the book's title, author in books.yml

    Args:
        book (ebooklib.epub.EpubBook): book object for the current book-id
        book_id (str): id of the book currently under processsing
    """
    # Get the book title
    if not books_dict[book_id]['meta']['bookName']:
        book_title = book.get_metadata('DC', 'title')[0][0]
        books_dict[book_id]['meta']['bookName'] = book_title
    else:
        print('Title already filled')

    # Get the book author
    if not books_dict[book_id]['meta']['authorName']:
        book_author = book.get_metadata('DC', 'creator')[0][0]
        books_dict[book_id]['meta']['authorName'] = book_author
    else:
        print('Author name already filled')

    # Add the meta data to the books.yml file
    config_system.update_books(books_dict)


def get_titles(book: ebooklib.epub.EpubBook) -> list:
    """Gets the titles in the book for generating the summary outline

    Args:
        book (ebooklib.epub.EpubBook): book object for the current book-id

    Returns:
        titles (list): all the titles that will section the summary
    """
    titles = list()

    # Get all the titles
    for item in book.toc:
        if isinstance(item, ebooklib.epub.Link):
            titles.append(item.title)
        elif isinstance(item, Tuple):
            for link in item[1]:
                if isinstance(link, Tuple):
                    for smaller_link in link[1]:
                        if isinstance(smaller_link, ebooklib.epub.Link):
                            titles.append(smaller_link.title)
                elif isinstance(link, ebooklib.epub.Link):
                    # print('here', link)
                    titles.append(link.title)

    # Remove the clutter
    clean_titles = list()
    # print('titles', titles)
    for title in titles:
        if 'chapter' in title.lower():
            clean_titles.append(title)

    # content_index = 0
    # for i, title in enumerate(titles):
    #     if 'content' in title.lower():
    #         content_index=i
    # titles = titles[content_index+1:]

    print('Titles: stored: ', clean_titles)
    return clean_titles


def get_original_text(raw_book_path: str, titles: list) -> dict:
    """Get the raw text and store it in a dictionary keyed by sections

    Args:
        raw_book_path (str): path to the raw format of the book
        titles (list): titles used to section the book

    Returns:
        dict: raw text in a dict keyed by sections
    """
    text_dict = dict()
    with open(raw_book_path) as file:
        lines = file.readlines()
        for line in lines:
            if line.strip() in titles:
                curr_title = line.strip()
                text_dict.setdefault(curr_title, '')
            elif len(text_dict) > 0:
                text_dict[curr_title] += line.replace('\n', ' ')

    return text_dict


def get_summary(text_dict: dict, ratio: float):
    """Summarizes the text in the dictionary

    Args:
        text_dict (dict): dictionary of original text keyed by chapters
        ratio (float): ratio of length of summary to length of original text

    Returns:
        dict: dictionary of summary text keyed by sections
    """
    # print('Length before summarization')
    # for k, v in text_dict.items():
    #     print(k, len(v))

    for k, v in text_dict.items():
        print(k, len(v))
        text_dict[k] = summarization.summarize(v, ratio=ratio)

    # print('Length after summarization')
    # for k, v in text_dict.items():
    #     print(k, len(v))

    return text_dict


def summarize(book_id: str, ratio: float):
    epub_file_path = books_dict[book_id]['files']['epub']
    book = epub.read_epub(epub_file_path)

    store_title_author(book, book_id)

    titles = get_titles(book)

    raw_book_path = books_dict[book_id]['files']['raw']

    original_text_dict = get_original_text(raw_book_path, titles)
    print('length of original text dict', len(original_text_dict))

    data_dir = config_system.load_paths_config()['data_dir']
    summary_text = os.path.join(data_dir, book_id, 'summary_' +
                                str(ratio) + '.txt')
    summary_json = os.path.join(data_dir, book_id, 'summary_' +
                                str(ratio) + '.json')

    if os.path.exists(summary_text) and len(original_text_dict) == 0:
        print("Text summary already exists or raw text \
            wasn't parsed correctly")
    else:
        # Get the summary
        print('-----Getting the summary-----')
        summary_text_dict = get_summary(original_text_dict, ratio)

        # Store the summary in .txt file
        print('Storing in .txt file')
        with open(summary_text, 'w') as file:
            for k, v in summary_text_dict.items():
                file.write(k)
                file.write('\n\n')
                file.write(v)
                file.write('\n\n')

        # Store the summary in .json file
        print('Storing in json file')
        json_file = open(summary_json, 'w')
        json.dump(summary_text_dict, json_file, indent=4)
        json_file.close()

        # Add the summary paths to books.yml
        books_dict[book_id]['files']['summary_text'] = summary_text
        books_dict[book_id]['files']['summary_json'] = summary_json

        config_system.update_books(books_dict)


def main():
    parser = argparse.ArgumentParser(
        description='Summarize the book with bookid provided')
    parser.add_argument(
        '--bookid',
        dest='book_id',
        type=str,
        help='Enter the book id which you want to summarize.',
        required=True
    )
    parser.add_argument(
        '--ratio',
        dest='ratio',
        type=float,
        help='Enter the ratio of lengths of summary text to the original text',
        required=False
    )
    args = parser.parse_args()
    summarize(args.book_id, args.ratio)


if __name__ == '__main__':
    main()
