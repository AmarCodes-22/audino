from pprint import pprint
import sys

from pkgs.utils import config_system

# load paths.yml into paths_dict
paths_dict = config_system.load_paths_config()

# load books.yml into books_dict
books_dict = config_system.load_books_config(paths_dict['books_config_file'])

# load audio.yml into audio_dict
audio_dict = config_system.load_audio_config(paths_dict['audio_config_file'])

# load summary.yml into summary_dict
summary_dict = config_system.load_summary_config(paths_dict['summary_config_file'])