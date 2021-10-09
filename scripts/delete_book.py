import argparse
from pprint import pprint


from pkgs.utils import config_system

paths_dict = config_system.load_paths_config()
books_dict = config_system.load_books_config(paths_dict['books_config_file'])

# pprint(books_dict)

def delete_book(book_id:str) -> None:
    books_dict.pop(book_id, None)
    # pprint(books_dict)
    config_system.update_books(books_dict, book_id=book_id, remove=True)

def main():
    parser = argparse.ArgumentParser(
        description='Delete a book and remove the entry from the books.yml file'
    )
    parser.add_argument(
        '--bookid',
        dest='book_id',
        type=str, 
        help='enter the book id', 
        required=True
    )
    args = parser.parse_args()
    delete_book(book_id=args.book_id)

if __name__ == '__main__':
    main()