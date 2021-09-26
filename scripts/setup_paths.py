import os 
from pprint import pprint

import yaml

def setup_paths_config():
    """Adds the major directories and config files to the paths.yml file"""
    # project root direcory
    project_root_dir = os.path.dirname(os.getcwd())

    # project_root_dir used for accessing data and configs dir
    data_dir = os.path.join(project_root_dir, 'data')
    configs_dir = os.path.join(project_root_dir, 'configs')

    # configs_dir used to access config files
    audio_config_file = os.path.join(configs_dir, 'audio.yml')
    books_config_file = os.path.join(configs_dir, 'books.yml')
    paths_config_file = os.path.join(configs_dir, 'paths.yml')
    summary_config_file = os.path.join(configs_dir, 'summary.yml')

    paths = {
        'project_root': project_root_dir, 
        'data_dir': data_dir, 
        'configs_dir': configs_dir,
        'audio_config_file': audio_config_file, 
        'books_config_file': books_config_file, 
        # 'paths_config_file': paths_config_file, 
        'summary_config_file': summary_config_file
    }

    with open(paths_config_file, 'w') as file:
        paths_dict = yaml.safe_dump(paths, file)

    with open(paths_config_file) as file:
        paths_dict = yaml.safe_load(file)
        pprint(paths_dict)


if __name__ == '__main__':
    setup_paths_config()

"""
todo: add a function that adds the paths to the paths config file
    add the following folders to the paths config file
    1. project root
    2. project_root/data
    3. project_root/configs
    4. project_root/configs/audio.yml
    5. project_root/configs/books.yml
    6. project_root/configs/paths.yml
    7. project_root/configs/summary.yml
"""
