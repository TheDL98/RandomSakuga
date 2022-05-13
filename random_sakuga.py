# Copyright (C) 2022 Ahmed Alkadhim
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

import requests
import schedule
import tenacity
import logging
import os
from sys import stdout
from time import strftime, gmtime, localtime, sleep
from tempfile import NamedTemporaryFile
from requests.exceptions import ConnectionError, Timeout

import logger_config
import apis
import process
import options


version = "V1.19-dev"

# Global variables
tag_summary_dict = {"version": None, "tags": []}

logger = logging.getLogger("logger_config")


def post():
    global tag_summary_dict
    sb_post = apis.get_sb_post(options.sb_limit, options.sb_tags)
    tag_summary_dict = apis.tag_summary(tag_summary_dict)
    artist, media = process.artist_and_media(sb_post["tags"], tag_summary_dict["tags"])

    fb_payload = process.create_fb_post_payload(
        sb_post["id"], artist, media, options.fb_access_token
    )
    temp_file_data = requests.get(sb_post["file_url"])
    # Create a temporary file
    with NamedTemporaryFile() as tf:
        tf.name = "dl_file." + sb_post["file_ext"]
        tf.write(temp_file_data.content)
        tf.seek(0)
        fb_post_id = apis.fb_video_post(options.fb_page_id, tf, fb_payload)
    if fb_post_id:
        # Check if media is western or not then query a database
        western_bool = True if "western" in sb_post["tags"] else False
        if media:
            # Search IMDb if media is western, MAL otherwise
            if western_bool:
                media_db_result = apis.imdb_search(media, options.imdb_api_key)
            else:
                media_db_result = apis.jikan_mal_search(media, options.jk_local_addr)

            if media_db_result:
                comment_payload = process.create_fb_comment(
                    western_bool, media_db_result
                )
                apis.fb_comment(options.fb_access_token, fb_post_id, comment_payload)

        logger.info(f"Facebook post ID: {fb_post_id}")

        if os.name == "posix":
            # Erase and go to beginning of line
            stdout.write("\033[2K\033[1G")
        post_feedback = (
            f"post({fb_post_id}) on {strftime('%d/%m/%Y, %H:%M:%S', localtime())}"
        )
        print(post_feedback)
        print(len(post_feedback) * "-", end="\n\n")


@tenacity.retry(
    retry=tenacity.retry_if_exception_type((ConnectionError, Timeout)),
    wait=tenacity.wait_exponential(multiplier=1, min=60, max=60 * 10),
    stop=tenacity.stop_after_attempt(5),
    reraise=True,
)
def main():
    # One post when the script starts if set to True
    if options.single_mode:
        post()

    # Scheduler setup
    if options.schedule_mode:
        schedule.every().day.at("00:00").do(post)
        schedule.every().day.at("06:00").do(post)
        schedule.every().day.at("12:00").do(post)
        schedule.every().day.at("18:00").do(post)
        while True:
            n = schedule.idle_seconds()
            if n > 0:
                if os.name == "posix":
                    # Erase and go to beginning of line
                    stdout.write("\033[2K\033[1G")
                print(f"Next post in: {strftime('%H:%M', gmtime(n))}", end="\r")
            sleep(60)
            schedule.run_pending()


if __name__ == "__main__":
    print(f"RandomSakuga {version}", end="\n\n")
    try:
        main()

    except (ConnectionError, Timeout):
        logger.critical("No Internet connection!")

    except KeyboardInterrupt:  # ! PyInstaller doesn't handle this well (PyInstaller #3646)
        print("\nInterrupt signal received!")
