import argparse
import os
from pprint import pprint

from gtts import gTTS

from pkgs.utils import config_system

paths_dict = config_system.load_paths_config()
books_dict = config_system.load_books_config(paths_dict['books_config_file'])
# pprint(books_dict)

def text_to_speech(book_id:str):
    """Get the audio of the summary for the bookid provided

    Args:
        book_id (str): bookid of the book currently under processing
    """
    # Get the summary file
    summary_file_path = books_dict[book_id]['files']['summary_text']
    ratio = summary_file_path.split('/')[-1][8:11]
    summary_file = open(summary_file_path)
    summary_file_content = summary_file.read()

    audio_obj_path = os.path.join(paths_dict['data_dir'], book_id,
                                  'audio_'+ratio+'.mp3')

    # add the audiobook path to the books.yml file
    books_dict[book_id]['files']['audio'] = audio_obj_path
    config_system.update_books(books_dict)

    if not os.path.exists(audio_obj_path):
        # Get the audio
        language='en'
        print('-----Started conversion-----')
        audio_obj = gTTS(text=summary_file_content, lang=language, slow=False)

        try:
            # Store the audio
            audio_obj.save(audio_obj_path)
            print('Conversion finished')

            # Add the audio to books.yml
            books_dict[book_id]['files']['audio'] = audio_obj_path
            config_system.update_books(books_dict)
        except:
            print('There is some error in uploading')
    else:
        books_dict[book_id]['files']['audio'] = audio_obj_path
        config_system.update_books(books_dict)
        print('Audio file for this book already exists')

def main():
    parser = argparse.ArgumentParser(
        description='Convert the summary to audio')
    parser.add_argument(
        '--bookid', 
        dest='book_id', 
        type=str, 
        help='Enter the book id for converting the summary to audio',
        required=True
    )
    args = parser.parse_args()
    text_to_speech(args.book_id)

if __name__ == '__main__':
    main()
