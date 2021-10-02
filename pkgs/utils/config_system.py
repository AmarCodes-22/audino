import os
from pathlib import Path
from pprint import pprint

import yaml

def load_paths_config():
    """Loads the paths.yml file and returns it as a dictionary"""
    # project root dir
    project_root = Path(__file__).parents[2]

    # configs dir
    configs_dir = os.path.join(project_root, 'configs')
    
    # path to the paths.yml file
    paths_config_file_path = os.path.join(configs_dir, 'paths.yml')

    # storing the contents of the config file into paths_dict
    with open (paths_config_file_path) as file:
        paths_dict = yaml.safe_load(file)

    return paths_dict

def load_books_config(books_config_path):
    """Loads the books.yml file and returns it as a dictionary"""

    with open(books_config_path) as file:
        books_dict = yaml.safe_load(file)

    return books_dict

def load_audio_config(audio_config_path):
    """Loads audio.yml file and returns it as a dictionary"""

    with open(audio_config_path) as file:
        audio_dict = yaml.safe_load(file)

    return audio_dict

def load_summary_config(summary_config_path):
    """Loads summary.yml file and returns it as a dictionary"""

    with open(summary_config_path) as file:
        summary_dict = yaml.safe_load(file)

    return summary_dict

def add_new_book(book_dict):
    paths_dict = load_paths_config()
    book_config_file = paths_dict['books_config_file']

    # read the current content of the yaml file
    with open(book_config_file) as file:
        curr_dict = yaml.safe_load(file)
        # print(books_dict)

    with open(book_config_file, 'w') as file:
        if curr_dict:
            curr_dict.update(book_dict)
            yaml.safe_dump(curr_dict, file)
        else:
            yaml.safe_dump(book_dict, file)

def load_firebase_config(firebase_config_path):
    """ Loads firebase config and returns it as a dictionary """

    with open(firebase_config_path) as file:
        firebase_config_dict = yaml.safe_load(file)

    return firebase_config_dict
