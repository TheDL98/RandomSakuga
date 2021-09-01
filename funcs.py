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

# Global variables
tag_summary_version: int = None
tag_summary_list: list = None


def get_sb_post(limit: int, tags: str):
    # Get random posts from Sakugabooru
    payload = {"limit": limit, "tags": tags}
    url = "https://www.sakugabooru.com/post.json"
    posts_response = requests.get(url, payload)

    # Select the highest scored post
    high_score = 0
    high_post: dict
    for post in posts_response.json():
        if post["score"] >= high_score:
            high_post, high_score = post, int(post["score"])
    return high_post


def tag_summary():
    global tag_summary_version
    global tag_summary_list
    # Request a summary json of all the tags on the site and convert it to a list
    url = "https://www.sakugabooru.com/tag/summary.json"
    tag_summary: dict = requests.get(url)
    if tag_summary_version != tag_summary.json()["version"]:
        tag_summary_version = tag_summary.json()["version"]
        tag_summary_list = tag_summary.json()["data"].split(" ")
        for i in range(len(tag_summary_list)):
            tag_summary_list[i] = tag_summary_list[i].split("`")
            tag_summary_list[i].remove("")
    return tag_summary_list


# Return the artist and the media names
def get_sb_artist_and_media(tags: str, tag_summary_list: list):
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
                    if not ("series" in tag):
                        media = tag.replace("_", " ").title()
                    elif not (media):
                        media = tag.replace("_", " ").title()
    return artist, media


# Use the Jikan unofficial MyAnimeList API to search for anime shows
def jikan_mal_search(media: str, tags: dict):
    if media and not ("western" in tags):
        jikan_payload = {"q": media, "limit": 1}
        jikan_url = "https://api.jikan.moe/v3/search/anime"
        try:
            jikan_response = requests.get(jikan_url, jikan_payload)
            if not jikan_response.ok:
                raise requests.HTTPError(
                    "{0[type]}: {0[status]}\n\t{0[message]}".format(
                        jikan_response.json()
                    )
                )
        except requests.HTTPError as e:
            print(e)
            return None
        mal_result = jikan_response.json()["results"][0]
        return mal_result
    return None


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


# Create a Facebook video post
def fb_video_post(page_id: str, file: bytes, payload: str):
    fb_post_url = f"https://graph.facebook.com/{page_id}/videos"
    fb_post_response = requests.post(fb_post_url, payload, files={"source": file})
    return int(fb_post_response.json()["id"])


# Create an FB comment with all the tags
def fb_MAL_comment(access_token: str, post_id: int, mal_info: str):
    mal_id = mal_info["mal_id"]
    mal_link = f"Possible MAL link: https://myanimelist.net/anime/{mal_id}"
    media_type = mal_info["type"]
    fb_comment_url = f"https://graph.facebook.com/{post_id}/comments"
    fb_comment_payload = {"access_token": access_token, "message": mal_link}
    fb_comment_response = requests.post(fb_comment_url, fb_comment_payload)
    return fb_comment_response.json()["id"]
