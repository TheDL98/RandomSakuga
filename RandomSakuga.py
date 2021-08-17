#############################################################################
# Copyright (C) Random Sakuga - All Rights Reserved                         #
# Written by Ahmed Alkadhim <ahmedalkadhim20001@gmail.com>, January 2021    #
#############################################################################

from schedule import every, run_pending
from time import strftime, localtime, sleep
from tempfile import NamedTemporaryFile
import requests
import json
import funcs


print("RandomSakuga V1.12\n")

# Load settings
with open("RS_settings.json") as f:
    data = json.load(f)

# general setting
single_mode = data["general"][0]["single_mode"]
continuous_mode = data["general"][0]["continuous_mode"]

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
    print(f"\npost id: {fb_post_id}")
    print(f"comment id: {fb_comment_id}")


# One post when the script starts if set to True
if single_mode:
    post()

# Continuous loop setup
if continuous_mode:
    every().day.at("00:00").do(post)
    every().day.at("06:00").do(post)
    every().day.at("12:00").do(post)
    every().day.at("18:00").do(post)

    while True:
        print(strftime("%H:%M", localtime()), end="\r")
        run_pending()
        sleep(60)  # wait one minute


# TODO: Maybe list alternative names of a media.
# TODO: Maybe post a comment with child sakugabooru posts links.
# TODO: possibly move Jikan result to the comment
# TODO: Generate settings file if none exist
