import os
from pathlib import Path

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

""" 
todo: add the following functions
    > load_audio_config
    > load_summary_config
"""