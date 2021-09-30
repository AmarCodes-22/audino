import argparse
import os
from pprint import pprint

from gtts import gTTS

from pkgs.utils import config_system

paths_dict = config_system.load_paths_config()
books_dict = config_system.load_books_config(paths_dict['books_config_file'])
# pprint(books_dict)

def tts(book_id:str):
    """ Get the audio for the summary of the book-id provided """
    # Get the summary file content
    summary_file_path = books_dict[book_id]['files']['summary']
    summary_file = open(summary_file_path)
    summary_file_content = summary_file.read()

    audio_obj_path = os.path.join(paths_dict['data_dir'], book_id, 'audio_20.mp3')
    if not os.path.exists(audio_obj_path):
        # Get the audio
        language='en'
        print('Started conversion')
        audio_obj = gTTS(text=summary_file_content, lang=language, slow=False)

        # Store the audio
        audio_obj.save(audio_obj_path)
        print('Conversion finished')

        # Add the audio to books.yml
        books_dict[book_id]['files']['audio'] = audio_obj_path
        config_system.add_new_book(books_dict)
    else:
        print('Audio file for this book already exists')

def main():
    parser = argparse.ArgumentParser(description='Convert the summary to audio')
    parser.add_argument(
        '--bookid', 
        dest='book_id', 
        type=str, 
        help='Enter the book id for which you want to convert the summary to audio', 
        required=True
    )
    args = parser.parse_args()
    tts(args.book_id)

if __name__ == '__main__':
    main()

"""todo
> Get the summary from the .txt file
> Use gtts to get the audio and store it in data/
> Add the audio file path to books.yml
"""