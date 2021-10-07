import argparse
import json
from pprint import pprint
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from pkgs.utils import config_system

paths_dict = config_system.load_paths_config()
books_dict = config_system.load_books_config(paths_dict['books_config_file'])
# pprint(books_dict)

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

DRIVE_BASE_URL = 'https://drive.google.com/file/d/'

def upload(book_id:str):
    """ Upload the files to drive """
    # Paths to the files to upload
    thumbnail_file_path = books_dict[book_id]['files']['thumbnail']
    summary_file_path = books_dict[book_id]['files']['summary']
    audio_file_path = books_dict[book_id]['files']['audio']

    # Get the audino folder
    audino_folder_id = ''
    file_list = drive.ListFile({
        'q': "'root' in parents and trashed=false"
    }).GetList()
    for file in file_list:
        if file['title'] == 'audino':
            audino_folder_id = file['id']
    # print(audino_folder_id)

    # Check if book_id folder already exists
    book_id_folder_exists = False
    location = "\'" + audino_folder_id + "\'" + " in parents and trashed=false"
    file_list = drive.ListFile({
        'q': location
    }).GetList()
    for file in file_list:
        if file['title'] == book_id:
            book_id_folder_exists = True

    if not book_id_folder_exists:
        # Create a book_id folder in the audino folder
        folder_name = book_id
        folder = drive.CreateFile({
            'title': folder_name, 
            'mimeType': 'application/vnd.google-apps.folder', 
            'parents': [{'id': audino_folder_id}]
        })
        folder.Upload()
    else:
        print('Folder already exists')

    # Get the folder id for the current book
    book_folder_id = ''
    location = "\'" + audino_folder_id + "\'" + " in parents and trashed=false"
    file_list = drive.ListFile({
        'q': location 
    }).GetList()
    for file in file_list:
        if file['title'] == book_id:
            book_folder_id = file['id']
    
    # Check if files already exist
    summary_20_exists = False
    thumbnail_exists = False
    audio_20_exists = False 
    location = "\'" + book_folder_id + "\'" + " in parents and trashed=false"
    file_list = drive.ListFile({
        'q': location
    }).GetList()
    for file in file_list:
        if file['title'] == 'summary_20.json':
            summary_20_exists = True
        if file['title'] == 'thumbnail.jpg':
            thumbnail_exists = True
        if file['title'] == 'audio_20.mp3':
            audio_20_exists = True

    # Upload summary
    if not summary_20_exists:
        summary_file = drive.CreateFile({
            'parents': [{'id': book_folder_id}], 
            'title': 'summary_20.json'
        })
        summary_file.SetContentFile(summary_file_path)
        print('Uploading summary')
        summary_file.Upload()
        summary_drive_link = DRIVE_BASE_URL + summary_file['id']
        books_dict[book_id]['meta_data']['SummaryUrl'] = summary_drive_link
    else:
        print('Summary already uploaded')

    # Upload thumbnail
    if not thumbnail_exists:
        thumbnail_file = drive.CreateFile({
            'parents': [{'id': book_folder_id}], 
            'title': 'thumbnail.jpg'
        })
        thumbnail_file.SetContentFile(thumbnail_file_path)
        print('Uploading thumbnail')
        thumbnail_file.Upload()
        thumbnail_drive_link = DRIVE_BASE_URL + thumbnail_file['id']
        books_dict[book_id]['meta_data']['ThumbnailUrl'] = thumbnail_drive_link
    else:
        print('Thumbnail already uploaded')

    # Upload audio
    if not audio_20_exists:
        audio_file = drive.CreateFile({
            'parents': [{'id': book_folder_id}], 
            'title': 'audio_20.mp3'
        })
        audio_file.SetContentFile(audio_file_path)
        print('Uploading audio')
        audio_file.Upload()
        audio_drive_link = DRIVE_BASE_URL + audio_file['id']
        books_dict[book_id]['meta_data']['AudioUrl'] = audio_drive_link
    else:
        print('Audio already uploaded')

    # Upload the information in books.yml
    config_system.add_new_book(books_dict)

    final_dict = dict()
    final_dict = books_dict[book_id]['meta_data']
    final_dict_path = os.path.join(paths_dict['data_dir'], book_id, 'final_drive.json')
    with open(final_dict_path, 'w') as file:
        json.dump(final_dict, file, indent=4)
    pprint(final_dict)

def main():
    parser = argparse.ArgumentParser(description='Upload the files to google-drive')
    parser.add_argument(
        '--bookid', 
        dest='book_id', 
        type=str, 
        help='enter the book-id for which you want to upload the files',
        required=True
    )
    args = parser.parse_args()
    upload(args.book_id)

    pass


if __name__ == '__main__':
    main()
