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

from time import strftime, localtime, sleep
from tempfile import NamedTemporaryFile
import requests
import json
import funcs

version = "V1.13-dev"
print(f"RandomSakuga {version}\n\n")

# Load settings
with open("RS_settings.json") as f:
    data = json.load(f)

# general setting
single_mode = data["general"][0]["single_mode"]
schedule_mode = data["general"][0]["continuous_mode"]

# Sakugabooru information
sb_tags = data["moebooru"][0]["tags"]
sb_limit = data["moebooru"][0]["limit"]

# facebook information
fb_access = data["facebook"][0]["access_token"]
fb_page_id = data["facebook"][0]["page_id"]


def post():
    sb_post = funcs.get_sb_post(sb_limit, sb_tags)
    tag_summary_list = funcs.tag_summary()
    artist, media = funcs.get_sb_artist_and_media(sb_post["tags"], tag_summary_list)
    # Disable until I find better solution
    # * mal_info = funcs.jikan_mal_search(media, sb_post["tags"])
    fb_message = funcs.format_fb_message(sb_post["id"], artist, media)
    # Title of the video
    title = "Sakugabooru post #" + str(sb_post["id"])
    try:
        # Create a temporary file
        temp_file = NamedTemporaryFile()
        temp_file.name = "dl_file." + sb_post["file_ext"]
        # Download data into the temp file
        file_data = requests.get(sb_post["file_url"], allow_redirects=True)
        temp_file.write(file_data.content)
        temp_file.seek(0)
        fb_post_id = funcs.fb_post(fb_page_id, fb_access, temp_file, fb_message, title)
    finally:
        # Free resources
        temp_file.close()
    fb_comment_id = funcs.fb_tags_comment(fb_access, fb_post_id, sb_post["tags"])
    post_feedback = (
        f"post({fb_post_id}) on {strftime('%d/%m/%Y, %H:%M:%S', localtime())}"
    )
    print(post_feedback)
    print(len(post_feedback) * "-" + "\n")


# One post when the script starts if set to True
if single_mode:
    post()

# Scheduler setup
if schedule_mode:
    while True:
        print(strftime("%H:%M", localtime()), end="\r")

        # Scheduler
        # Post every six hours at (00:00, 06:00, ...)
        hour_ = localtime().tm_hour % 6
        minute = localtime().tm_min
        if hour_ == 0 and minute == 0:
            post()
        sleep(60)  # wait one minute


# TODO: Maybe list alternative names of a media.
# TODO: Maybe post a comment with child sakugabooru posts links.
# TODO: possibly move Jikan result to the comment
# TODO: Generate settings file if none exist
