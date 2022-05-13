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

import re
import logging

import logger_config


logger = logging.getLogger("logger_config")


def titlecase(s: str) -> str:
    return re.sub(
        r"[A-Za-z]+('[A-Za-z]+)?", lambda mo: mo.group()[0].upper() + mo.group()[1:], s
    )


def formated_title(s):
    upper_roman_num = re.sub(r"\b(ix|iv|v?i{0,3})\b", lambda mo: mo.group().upper(), s)
    return titlecase(upper_roman_num)


# Return the artist and the media names
def artist_and_media(tags: str, tag_summary_list: list) -> tuple[list, str]:
    tags = tags.split(" ")
    artist = []
    media: str = None
    # Search through summary_list to find artist and media
    for tag in tags:
        for summary_tag in tag_summary_list:
            if tag in summary_tag[1:]:
                if summary_tag[0] == "1":
                    if tag != "artist_unknown":
                        artist.append(titlecase(tag.replace("_", " ")))
                    else:
                        artist.append("Unknown Animator/s")
                elif summary_tag[0] == "3":
                    # Favor media tags without "series" in them
                    if "series" not in tag:
                        media = formated_title(tag.replace("_", " "))
                    elif not media:
                        media = formated_title(tag.replace("_", " "))
    return artist, media


# Create the message to be posted on FB
def create_fb_post_payload(
    sb_post_id: str, sb_artists: list, sb_media: str, access_token: str
) -> dict[str, any]:
    # Message
    sb_artists = ", ".join(sb_artists)
    message = f"Key animation: {sb_artists}"
    if sb_media is not None:
        message += f"\nTV/Movie/Other: {sb_media}"
    message += f"\nhttps://www.sakugabooru.com/post/show/{sb_post_id}"
    # Title of the video
    title = f"Sakugabooru post #{sb_post_id}"
    payload = {
        "access_token": access_token,
        "description": message.encode("UTF-8", "strict"),
        "content_category": "ENTERTAINMENT",
        "title": title,
    }
    return payload


def create_fb_comment(western_switch: bool, media_db_result: dict) -> str:
    if western_switch:
        imdb_id = media_db_result["id"]
        return f"Possible IMDb link: \nhttps://www.imdb.com/title/{imdb_id}"
    else:
        mal_id = media_db_result["mal_id"]
        return f"Possible MAL link: \nhttps://myanimelist.net/anime/{mal_id}"
