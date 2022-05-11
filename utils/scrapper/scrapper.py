import sys
import os
import requests
import hashlib
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


URL = "https://www.cameo.com/"
NEWLINE = "\n"
SHA256SUMS = "SHA256SUMS"
MAX_TOKEN_LINES = 91
TOKEN_ENCODING = "utf-8"
BACKUP = "backup.html"
SOUP_PARSER = "lxml"
STAR_CARD_TAG = "div"
STAR_CARD_SELECTOR = "data-testid"
STAR_CARD_VALUE = "undefined-StarCard"
PROFILE_IMAGE_TAG = "img"
PROFILE_IMAGE_CLASS = "css-9pa8cd"
TALENT_NAME_TAG = "div"
TALENT_NAME_SELECTOR = "data-testid"
TALENT_NAME_VALUE = "talent-name"
LIMIT = 30
IMAGE_HEIGHT = 320
JSON_IMAGE_ATTR = "profile_image"
JSON_NAME_ATTR = "talent_name"
JSON_PROFESSION_ATTR = "talent_profession"
DUMP_FILE = "../../src/assets/data/talent.json"


def get_dynamic_page_source(hash):
    chrome_options = Options()

    # FIXME: Issue #1234: Adding --headless, --disable-extensions, and --disable-gpu options caused selenium to not fetch complete page source
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    page_source = driver.page_source
    driver.quit()

    with open(BACKUP, "w") as file:
        file.write(page_source)
        file.close()

    with open(SHA256SUMS, "w") as file:
        file.write(hash)
        file.close()

    return page_source


def get_backup_page_source():
    with open(BACKUP, "r") as file:
        page_source = file.read()
        file.close()

        return page_source


def get_page_source(only_backup=False):
    if only_backup:
        return get_backup_page_source()

    token = NEWLINE.join(requests.get(URL).text.split(NEWLINE)[:MAX_TOKEN_LINES]).encode(TOKEN_ENCODING)
    hash = hashlib.sha256(token).hexdigest()

    request_selenium = False

    # Request selenium for a fresh page source if either of the following three conditions are met:
    # 1) SHA256SUMS does not exist
    # 2) SHA256SUMS exists but does not match the current hash
    # 3) BACKUP does not exist

    # Do NOT request selenium if SHA256SUMS exists and matches, and BACKUP exists

    if os.path.isfile(SHA256SUMS):
        with open(SHA256SUMS, "r") as file:
            sha256sums = file.read()

            if sha256sums != hash:
                request_selenium = True

            file.close()
    else:
        request_selenium = True

    if not os.path.isfile(BACKUP):
        request_selenium = True

    return get_dynamic_page_source(hash) if request_selenium else get_backup_page_source()


def is_star_card(tag):
    return tag.name == STAR_CARD_TAG and tag.has_attr(STAR_CARD_SELECTOR) and tag.get(STAR_CARD_SELECTOR) == STAR_CARD_VALUE and tag.find(PROFILE_IMAGE_TAG, class_=PROFILE_IMAGE_CLASS) is not None


def get_talent_list(page_source):
    soup = BeautifulSoup(page_source, SOUP_PARSER)
    star_cards = soup.find_all(is_star_card, limit=LIMIT)

    talent_list = []

    for star_card in star_cards:
        profile_image_element = star_card.find(PROFILE_IMAGE_TAG, class_=PROFILE_IMAGE_CLASS)
        profile_image = profile_image_element.get("src")
        query_start = profile_image.rfind("?")
        height_start = profile_image.find("=", query_start)
        height_end = profile_image.find("&", query_start)
        height = str(IMAGE_HEIGHT)
        profile_image = profile_image[:height_start + 1] + height + profile_image[height_end:]

        talent_name_element = star_card.find(TALENT_NAME_TAG, attrs={TALENT_NAME_SELECTOR: TALENT_NAME_VALUE})
        talent_name = talent_name_element.string.strip()

        talent_profession_element = talent_name_element.next_sibling
        talent_profession = talent_profession_element.string.strip()

        talent = {}
        talent[JSON_IMAGE_ATTR] = profile_image
        talent[JSON_NAME_ATTR] = talent_name
        talent[JSON_PROFESSION_ATTR] = talent_profession
        talent_list.append(talent)

    return talent_list


def dump_json(talent_list):
    with open(DUMP_FILE, "w") as file:
        json.dump(talent_list, file, indent=2)


def main():
    # FIXME: Temporarily disabled fetching from selenium because of issue: 1234

    page_source = get_page_source(only_backup=True)
    talent_list = get_talent_list(page_source)
    dump_json(talent_list)

    return 0


if __name__ == "__main__":
    sys.exit(main())
