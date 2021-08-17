#############################################################################
# Copyright (C) Random Sakuga - All Rights Reserved                         #
# Written by Ahmed Alkadhim <ahmedalkadhim20001@gmail.com>, January 2021    #
#############################################################################

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
    if not ("western" in tags):
        jikan_payload = {"q": media, "limit": 1}
        jikan_url = "https://api.jikan.moe/v3/search/anime"
        jikan_response = requests.get(jikan_url, jikan_payload)
        mal_result = jikan_response.json()["results"][0]
        return mal_result
    return False


# Create the message to be posted on FB
def format_fb_message(
    sb_post_id: str,
    sb_artists: list,
    sb_media: str,
    mal_info: str = False,
):
    if mal_info:
        mal_id = mal_info["mal_id"]
        mal_link = f"https://myanimelist.net/anime/{mal_id}"
        media_type = mal_info["type"]

    sb_artists = ", ".join(sb_artists)
    message = f"Key animation: {sb_artists}"
    if sb_media is not None:
        if mal_info:
            if media_type == "TV":
                message += f"\n{media_type} show: "
            elif media_type == "Music":
                message += f"\n{media_type} video: "
            else:
                message += f"\n{media_type}: "
        else:
            message += f"\nTV/Movie/Other: "
        message += sb_media
    message += f"\nhttps://www.sakugabooru.com/post/show/{sb_post_id}"
    if mal_info:
        message += f"\n{mal_link}"
    return message


# Create a Facebook post
def fb_post(page_id: int, access_token: str, file: bytes, message: str, title: str):
    fb_post_url = f"https://graph.facebook.com/{page_id}/videos"
    fb_post_files = {"source": file}
    fb_post_payload = {
        "access_token": access_token,
        "description": message.encode("UTF-8", "strict"),
        "content_category": "ENTERTAINMENT",
        "title": title,
    }
    fb_post_response = requests.post(fb_post_url, fb_post_payload, files=fb_post_files)
    return int(fb_post_response.json()["id"])


# Create an FB comment with all the tags
def fb_tags_comment(access_token: str, post_id: int, tags: str):
    tags = tags.replace(" ", ", ")
    fb_comment_url = f"https://graph.facebook.com/{post_id}/comments"
    fb_comment_payload = {"access_token": access_token, "message": tags}
    fb_comment_response = requests.post(fb_comment_url, fb_comment_payload)
    return fb_comment_response.json()["id"]
