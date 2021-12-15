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

import requests
import logging
import os
from sys import stdout
from time import strftime, localtime, sleep
from tempfile import NamedTemporaryFile

import logger_config
import apis
import process
import options


# Global variables
tag_summary_dict = {"version": None, "tags": []}

def main():
    logger = logging.getLogger("logger_config")

    version = "V1.18-dev"
    print(f"RandomSakuga {version}", end="\n\n")

    def post():
        global tag_summary_dict
        sb_post = apis.get_sb_post(options.sb_limit, options.sb_tags)
        tag_summary_dict = apis.tag_summary(tag_summary_dict)
        artist, media = process.artist_and_media(
            sb_post["tags"], tag_summary_dict["tags"]
        )
        mal_info = apis.jikan_mal_search(media, sb_post["tags"], options.jk_local_addr)
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
            if mal_info:
                apis.fb_MAL_comment(
                    options.fb_access_token, fb_post_id, mal_info["mal_id"]
                )

            logger.info(f"Facebook post ID: {fb_post_id}")
            post_feedback = (
                f"post({fb_post_id}) on {strftime('%d/%m/%Y, %H:%M:%S', localtime())}"
            )
            print(post_feedback)
            print(len(post_feedback) * "-", end="\n\n")

    try:
        # One post when the script starts if set to True
        if options.single_mode:
            post()

        # Scheduler setup
        if options.schedule_mode:
            while True:
                if os.name == "posix":
                    stdout.write("\033[2K\033[1G")  # Erase and go to beginning of line
                print(strftime("%H:%M", localtime()), end="\r")

                # Scheduler
                # Post every six hours at (00:00, 06:00, ...)
                hour_ = localtime().tm_hour % 6
                minute = localtime().tm_min
                if hour_ == 0 and minute == 0:
                    post()
                sleep(60)  # wait one minute
    except KeyboardInterrupt:  # ! PyInstaller doesn't handle this well (PyInstaller #3646)
        print("\nInterrupt signal received!")


if __name__ == "__main__":
    main()
