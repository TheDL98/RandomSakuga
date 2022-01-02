# Copyright (C) 2021 Ahmed Alkadhim
#
# This file is part of Random Sakuga.
#
# Random Sakuga is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Random Sakuga is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Random Sakuga.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging
import configparser
from pathlib import Path
from sys import exit

import logger_config


logger = logging.getLogger("logger_config")


class ConfigFileError(Exception):
    """File not found, Empty or corrupt"""


description = "Python script that posts random sakuga to Facebook"
parser = argparse.ArgumentParser(prog="RandomSakuga", description=description)

default_config_file = "RS_config.ini"
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
    logger.critical("File not found, Empty or corrupt")
    exit()


try:
    # general settings
    general = config["general"]
    single_mode = general.getboolean("single_mode")
    schedule_mode = general.getboolean("continuous_mode")

    # Sakugabooru settings
    moebooru = config["moebooru"]
    sb_tags = moebooru["tags"]
    sb_limit = moebooru["limit"]

    # IMDb settings
    imdb_api = config["imdb-api"]
    imdb_api_key = imdb_api["api_key"]

    # Jikan settings
    jikan = config["jikan"]
    if jikan.getboolean("enable_local_address"):
        jk_local_addr = jikan["local_address"]
    else:
        jk_local_addr = False

    # facebook settings
    facebook = config["facebook"]
    fb_access_token = facebook["access_token"]
    fb_page_id = facebook["page_id"]
except KeyError as e:
    logger.critical(f"Key {e} does not exist")
    exit()
