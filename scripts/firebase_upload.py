import argparse
from pprint import pprint

from pkgs.utils import config_system

import pyrebase

paths_dict = config_system.load_paths_config()
books_dict = config_system.load_books_config(paths_dict['books_config_file'])

firebase_config = config_system.load_firebase_config(paths_dict['firebase_config_file'])

firebase = pyrebase.initialize_app(firebase_config)
storage = firebase.storage()

def upload(book_id:str):
    """ Uploads the files to firebase and adds the url to the books.yml meta_data """

    # Get files to upload
    audio_file = books_dict[book_id]['files']['audio']
    summary_file = books_dict[book_id]['files']['summary_json']
    thumbnail_file = books_dict[book_id]['files']['thumbnail']

    # Upload audio
    local_filename = audio_file
    cloud_filename = book_id + '/' + local_filename.split('/')[-1]
    storage.child(cloud_filename).put(local_filename)
    firebase_url = storage.child(cloud_filename).get_url(None)
    books_dict[book_id]['meta']['AudioUrl'] = firebase_url

    # Upload summary
    local_filename = summary_file
    cloud_filename = book_id + '/' + local_filename.split('/')[-1]
    storage.child(cloud_filename).put(local_filename)
    firebase_url = storage.child(cloud_filename).get_url(None)
    books_dict[book_id]['meta']['SummaryUrl'] = firebase_url

    # Upload thumbnail
    local_filename = thumbnail_file
    cloud_filename = book_id + '/' + local_filename.split('/')[-1]
    storage.child(cloud_filename).put(local_filename)
    firebase_url = storage.child(cloud_filename).get_url(None)
    books_dict[book_id]['meta']['ThumbnailUrl'] = firebase_url

    config_system.update_books(books_dict)

    final_dict = books_dict[book_id]['meta']
    # Later send this with the post api
    pprint(final_dict)

    # final_dict = dict()
    # # fuck them, i'll just upload the complete folder
    # book_id_folder = os.path.join(paths_dict['data_dir'], book_id)
    # for dirpath, dirnames, filenames in os.walk(book_id_folder):
    #     for filename in filenames:
    #         local_filename = os.path.join(dirpath, filename)
    #         cloud_filename = book_id + '/' + filename
    #         storage.child(cloud_filename).put(local_filename)
    #         print(storage.child(cloud_filename).get_url(None))
            # print(file)

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
