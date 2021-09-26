import argparse
from pprint import pprint
import sys

from pkgs.utils import config_system

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
    print(args.book_id)

# load the configs into respective dicts
paths_dict = config_system.load_paths_config()
books_dict = config_system.load_books_config(paths_dict['books_config_file'])
audio_dict = config_system.load_audio_config(paths_dict['audio_config_file'])
summary_dict = config_system.load_summary_config(paths_dict['summary_config_file'])

# checking out argparse

if __name__ == '__main__':
    main()

"""todo
    > add a function to download the epub and raw text and put it inside data/book_id/ 
    > add a function to get the thumbnail 
    > add a function to get the genre
    > add a function to add the book to the books.yml file
"""