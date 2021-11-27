import argparse
from pprint import pprint

from pkgs.utils import config_system

import pyrebase

# load paths, books in a dictionary
paths_dict = config_system.load_paths_config()
books_dict = config_system.load_books_config(paths_dict['books_config_file'])

firebase_config = config_system.load_firebase_config(
    paths_dict['firebase_config_file'])

firebase = pyrebase.initialize_app(firebase_config)
storage = firebase.storage()


def upload(book_id: str):
    """Uploads the files to firebase, add the firebase urls to meta-data

    Args:
        book_id (str): book-id for the book currently under processing
    """

    # Get files to upload
    audio_file = books_dict[book_id]['files']['audio']
    summary_file = books_dict[book_id]['files']['kshitij_json']
    # summary_file = '/home/amar/projects/audino/data/2554/kshitij.json'
    thumbnail_file = books_dict[book_id]['files']['thumbnail']

    # Upload audio
    local_filename = audio_file
    cloud_filename = book_id + '/' + local_filename.split('/')[-1]
    storage.child(cloud_filename).put(local_filename)
    firebase_url = storage.child(cloud_filename).get_url(None)
    books_dict[book_id]['meta']['audioUrl'] = firebase_url

    # Upload summary
    local_filename = summary_file
    # cloud_filename = book_id + '/' + local_filename.split('/')[-1]
    cloud_filename = book_id + '/' + 'kshitij.json'
    storage.child(cloud_filename).put(local_filename)
    firebase_url = storage.child(cloud_filename).get_url(None)
    books_dict[book_id]['meta']['summaryUrl'] = firebase_url

    # Upload thumbnail
    local_filename = thumbnail_file
    cloud_filename = book_id + '/' + local_filename.split('/')[-1]
    storage.child(cloud_filename).put(local_filename)
    firebase_url = storage.child(cloud_filename).get_url(None)
    books_dict[book_id]['meta']['thumbnailUrl'] = firebase_url

    config_system.update_books(books_dict)

    final_dict = books_dict[book_id]['meta']
    # Later send this with the post api
    pprint(final_dict)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bookid',
        dest='book_id',
        type=str,
        help='Enter the book id for which you want to upload the data',
        required=True
    )
    args = parser.parse_args()
    upload(args.book_id)


if __name__ == '__main__':
    main()
