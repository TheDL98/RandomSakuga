import re
import logging
from jikanpy import Jikan

import random_sakuga.logger_config as logger_config
import random_sakuga.apis as apis
import random_sakuga.options as options


logger = logging.getLogger("logger_config")


def titlecase(s: str) -> str:
    return re.sub(
        r"[A-Za-z]+('[A-Za-z]+)?", lambda mo: mo.group()[0].upper() + mo.group()[1:], s
    )


def formatted_title(s) -> str:
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
                        media = formatted_title(tag.replace("_", " "))
                    elif not media:
                        media = formatted_title(tag.replace("_", " "))
    return artist, media


# Create the message to be posted on FB
def create_fb_post_payload(
    sb_post_id: str,
    sb_artists: list,
    sb_media: str,
    media_db_result: str,
    access_token: str,
) -> dict[str, any]:
    # Message
    sb_artists = ", ".join(sb_artists)
    message = f"Key animation: {sb_artists}"
    if sb_media is not None:
        message += f"\nTV/Movie/Other: {sb_media}"
    message += f"\nhttps://www.sakugabooru.com/post/show/{sb_post_id}"
    if media_db_result is not None:
        message += f"\n\n{media_db_result}"
    # Title of the video
    title = f"Sakugabooru post #{sb_post_id}"
    payload = {
        "access_token": access_token,
        "description": message.encode("UTF-8", "strict"),
        "content_category": "ENTERTAINMENT",
        "title": title,
    }
    return payload


def media_databases(tags: str, sb_media: str) -> str:
    # Check if media is western or not then query a database
    western_bool = True if "western" in tags else False
    if options.imdb_enable and western_bool:
        imdb_id = apis.imdb_search(sb_media, options.imdb_api_key)["id"]
        return f"Possible IMDb link: \nhttps://www.imdb.com/title/{imdb_id}"
    elif options.jikan_enable and not western_bool:
        #! Deprecated
        # mal_id = apis.jikan_mal_search(sb_media, options.jk_local_addr)["mal_id"]
        #
        
        if options.jk_local_addr:
            jikan = Jikan(selected_base=options.jk_local_addr)
        else:
            jikan = Jikan()
        mal_id = jikan.search("anime", sb_media, parameters={"limit":1})["data"][0]["mal_id"]
        return f"Possible MAL link: \nhttps://myanimelist.net/anime/{mal_id}"
