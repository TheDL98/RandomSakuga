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

from pathlib import Path
from sys import exit
import argparse
import logging
import json


default_json_file = "RS_settings.json"
logger = logging.getLogger("__main__")


description = "Python script that posts random sakuga to Facebook"
parser = argparse.ArgumentParser(prog="RandomSakuga", description=description)

parser.add_argument(
    "-c",
    "--config",
    type=Path,
    help="path to configuration file",
    default=default_json_file,
)
args = parser.parse_args()


# Load settings
try:
    json_file = args.config
    f = open(json_file)
except FileNotFoundError:
    logger.critical(f'file "{json_file}" does not exist!')
    exit()
else:
    try:
        data = json.load(f)
    except json.JSONDecodeError as e:
        logger.critical("JSON file is empty or corrupt!")
        logger.critical(f"Reported error: {e}")
        exit()
    finally:
        f.close()

try:
    # general setting
    single_mode = data["general"][0]["single_mode"]
    schedule_mode = data["general"][0]["continuous_mode"]
    root_logger = data["general"][0]["debug_logger"]

    # Sakugabooru information
    sb_tags = data["moebooru"][0]["tags"]
    sb_limit = data["moebooru"][0]["limit"]
    
    # Jikan options
    if data["jikan"][0]["enable_jikan_local_address"]:
        jk_local_addr = data["jikan"][0]["local_address"]
    else:
        jk_local_addr = False

    # facebook information
    fb_access_token = data["facebook"][0]["access_token"]
    fb_page_id = data["facebook"][0]["page_id"]
except KeyError as e:
    logger.critical(f"Key {e} does not exist")
    exit()
