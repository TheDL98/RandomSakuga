# Copyright (C) 2023 Ahmed Alkadhim
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


version = "V1.21-beta"

# Global variables
tag_summary_dict = {"version": None, "tags": []}

logger = logging.getLogger("logger_config")


def post() -> None:
    global tag_summary_dict
    sb_post = apis.get_sb_post(options.sb_limit, options.sb_tags)
    tag_summary_dict = apis.tag_summary(tag_summary_dict)
    artist, media = process.artist_and_media(sb_post["tags"], tag_summary_dict["tags"])
    if media:
        media_db_result = process.media_databases(sb_post["tags"], media)
    else:
        media_db_result = None
    fb_payload = process.create_fb_post_payload(
        sb_post["id"], artist, media, media_db_result, options.fb_access_token
    )
    temp_file_data = requests.get(sb_post["file_url"])
    # Create a temporary file
    with NamedTemporaryFile() as tf:
        tf.name = "dl_file." + sb_post["file_ext"]
        tf.write(temp_file_data.content)
        tf.seek(0)
        if options.fb_enable:
            fb_post_id = apis.fb_video_post(options.fb_page_id, tf, fb_payload)

            if fb_post_id:
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
def main() -> None:
    # One post when the script starts if set to True
    if options.single_mode:
        post()

    # Scheduler setup
    if options.schedule_mode:
        schedule.every().day.at(options.post_time).do(post)
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

    except (
        KeyboardInterrupt
    ):  # ! PyInstaller doesn't handle this well (PyInstaller #3646)
        print("\nInterrupt signal received!")
