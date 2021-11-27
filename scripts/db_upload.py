import argparse
from pprint import pprint

from pkgs.utils import config_system

import requests
import json

paths_dict = config_system.load_paths_config()

genre_url = 'https://audino.herokuapp.com/genre'
book_url = 'https://audino.herokuapp.com/book'

#! post new genre (use only for new genres)
genreName = "Crime"
genre_dict = {"genreName": genreName}
# requests.post(genre_url, json=genre_dict)

#* get the genreid matching the genre
all_data = requests.get(genre_url)
all_data_dict = json.loads(all_data.content.decode('ascii'))
curr_genre_id = None
for genre in all_data_dict['genres']:
    if genre["genreName"] == genreName:
        curr_genre_id = genre['_id']
        break
    # print('---------------------------------')

#* post the final_dict
def upload(book_id: str):
    final_dict = dict()
    books_dict = config_system.load_books_config(paths_dict['books_config_file'])
    final_dict['bookId'] = book_id
    final_dict['bookName'] = books_dict[book_id]['meta']['bookName']
    final_dict['authorName'] = books_dict[book_id]['meta']['authorName']
    final_dict['thumbnailUrl'] = books_dict[book_id]['meta']['thumbnailUrl']
    final_dict['audioUrl'] = books_dict[book_id]['meta']['audioUrl']
    final_dict['Description'] = "" 
    final_dict['SummaryText'] = books_dict[book_id]['files']['kshitij_json']
    final_dict['genre'] = curr_genre_id

    # send the details to the database
    requests.post(book_url, json=final_dict)

def main():
    parser = argparse.ArgumentParser(
        description='Update details about the book with bookid provided')
    parser.add_argument(
        '--bookid',
        dest='book_id',
        type=str,
        help='Enter the book id which you want to summarize.',
        required=True
    )
    args = parser.parse_args()
    upload(args.book_id)


if __name__ == '__main__':
    main()
