import requests
import logging
from urllib.parse import urljoin

import random_sakuga.logger_config as logger_config


logger = logging.getLogger("logger_config")


def get_sb_post(limit: int, tags: str) -> dict:
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
    logger.info(f"Sakuga Booru post ID: {high_post['id']}")
    return high_post


def tag_summary(prev_tag_summary: dict) -> dict:
    # Request a summary json of all the tags on the site and convert it to a list
    url = "https://www.sakugabooru.com/tag/summary.json"
    tag_summary: dict = requests.get(url)
    if prev_tag_summary["version"] != tag_summary.json()["version"]:
        prev_tag_summary["version"] = tag_summary.json()["version"]
        prev_tag_summary["tags"] = tag_summary.json()["data"].split(" ")
        for i in range(len(prev_tag_summary["tags"])):
            prev_tag_summary["tags"][i] = prev_tag_summary["tags"][i].split("`")
            prev_tag_summary["tags"][i].remove("")
    return prev_tag_summary


# Query IMDb using imdb-api.com
def imdb_search(media: str, api_key: str) -> dict | None:
    url = f"https://imdb-api.com/en/API/AdvancedSearch/{api_key}"
    payload = {"title": media, "genres": "animation", "count": "1"}
    try:
        imdb_result = requests.get(url, payload)
        return imdb_result.json()["results"][0]
    except IndexError:
        return None


# Use the Jikan unofficial MyAnimeList API to search for anime shows
# ! Deprecated
def jikan_mal_search(media: str, jikan_local_address: str | bool) -> dict | None:
    default_url = "https://api.jikan.moe/v4/anime"
    try:
        if jikan_local_address:
            requests.get(jikan_local_address)
            url = urljoin(jikan_local_address, "v4/anime")
        else:
            url = default_url
    except requests.exceptions.ConnectionError:
        logger.error(
            "No connection to your local Jikan API. "
            "Make sure your server is up and the address is correct."
        )
        url = default_url

    payload = {"q": media, "limit": 1}
    try:
        jikan_response = requests.get(url, payload)
        if not jikan_response.ok:
            raise requests.HTTPError(
                "{0[type]}: {0[status]}\n\t{0[message]}".format(jikan_response.json())
            )
        mal_result = jikan_response.json()["data"][0]
        return mal_result
    except requests.HTTPError as e:
        logger.error(e)
        return None


# Create a Facebook video post
def fb_video_post(page_id: str, file: bytes, payload: str) -> int | None:
    url = f"https://graph.facebook.com/{page_id}/videos"
    try:
        fb_post_response = requests.post(url, payload, files={"source": file})
        if not fb_post_response.ok:
            raise requests.HTTPError(
                "{0[type]}: {0[code]}\n\t{0[message]}".format(
                    fb_post_response.json()["error"]
                )
            )
        return int(fb_post_response.json()["id"])
    except requests.HTTPError as e:
        logger.error(e)
        return None


# Create an FB comment  # ! Disabled
def fb_comment(access_token: str, post_id: int, comment: str) -> str:
    fb_comment_url = f"https://graph.facebook.com/{post_id}/comments"
    fb_comment_payload = {"access_token": access_token, "message": comment}
    fb_comment_response = requests.post(fb_comment_url, fb_comment_payload)
    return fb_comment_response.json()["id"]
