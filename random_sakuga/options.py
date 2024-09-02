import platformdirs
import argparse
import logging
import os
import configparser
from pathlib import Path
from sys import exit

import logger_config


logger = logging.getLogger("logger_config")


class ConfigFileError(Exception):
    """File not found, Empty or corrupt"""


description = "Python script that posts random sakuga to Facebook"
parser = argparse.ArgumentParser(prog="RandomSakuga", description=description)


# Check if the config file is in the user's config directory otherwise use current working directory
default_config_file = os.path.join(platformdirs.user_config_dir(), "random_sakuga.ini")
if not os.path.isfile(default_config_file):
    default_config_file = "./random_sakuga.ini"

parser.add_argument(
    "-c",
    "--config",
    type=Path,
    help="path to configuration file",
    default=default_config_file,
)
args = parser.parse_args()

# Load settings
try:
    config_file = args.config
    config = configparser.ConfigParser()
    config.read(config_file)
    if config.sections() == []:
        raise ConfigFileError
except ConfigFileError:
    logger.critical("Config file not found, empty or invalid")
    exit()


try:
    # general settings
    general = config["general"]
    single_mode = general.getboolean("single_mode")
    schedule_mode = general.getboolean("continuous_mode")
    post_time = general.get("post_time")

    # Sakugabooru settings
    moebooru = config["moebooru"]
    sb_tags = moebooru["tags"]
    sb_limit = moebooru["limit"]

    # IMDb settings
    imdb_api = config["imdb-api"]
    imdb_enable = imdb_api.getboolean("imdb_enable")
    if imdb_enable:
        imdb_api_key = imdb_api["api_key"]

    # Jikan settings
    jikan = config["jikan"]
    jikan_enable = jikan.getboolean("jikan_enable")
    if jikan_enable:
        if jikan.getboolean("enable_local_address"):
            jk_local_addr = jikan["local_address"]
        else:
            jk_local_addr = False

    # facebook settings
    facebook = config["facebook"]
    fb_enable = facebook.getboolean("facebook_enable")
    fb_access_token = facebook["access_token"]
    fb_page_id = facebook["page_id"]
except KeyError as e:
    logger.critical(f"Key {e} does not exist")
    exit()
