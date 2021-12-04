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

import logging


logger = logging.getLogger("__main__")


# Return the artist and the media names
def artist_and_media(tags: str, tag_summary_list: list):
    tags = tags.split(" ")
    artist = []
    media: str = None
    # Search through summary_list to find artist and media
    for tag in tags:
        for summary_tag in tag_summary_list:
            if tag in summary_tag[1:]:
                if summary_tag[0] == "1":
                    if tag != "artist_unknown":
                        artist.append(tag.replace("_", " ").title())
                    else:
                        artist.append("Unknown Animator/s")
                elif summary_tag[0] == "3":
                    # Try to favor media tags without "series" in them
                    if "series" not in tag:
                        media = tag.replace("_", " ").title()
                    elif not media:
                        media = tag.replace("_", " ").title()
    return artist, media


# Create the message to be posted on FB
def create_fb_post_payload(
    sb_post_id: str, sb_artists: list, sb_media: str, access_token: str
):
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
