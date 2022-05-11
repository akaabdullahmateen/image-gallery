import sys
import os
import requests
import hashlib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


URL = "https://www.cameo.com/"
SHA256SUMS = "SHA256SUMS"
BACKUP = "backup.html"
PROFILE_IMAGE_CLASS = "css-9pa8cd"


def get_dynamic_page_source(hash):
    print("Adding \"--headless\", \"--disable-extensions\", \"--disable-gpu\" arguments to chrome options")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")

    print("Starting chrome browser in headless state")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)
    page_source = driver.page_source
    print("Shutting down chrome and webdriver")
    driver.quit()

    print("Writing fetched page source to BACKUP file")
    with open(BACKUP, "w") as file:
        file.write(page_source)
        file.close()

    print("Writing current hash to SHA256SUMS file")
    with open(SHA256SUMS, "w") as file:
        file.write(hash)
        file.close()

    return page_source


def get_backup_page_source():
    print("Reading page source from BACKUP file")
    with open(BACKUP, "r") as file:
        page_source = file.read()
        file.close()

        return page_source


def get_page_source():
    print("Creating token and hash from requests GET method")
    token = "\n".join(requests.get(URL).text.split("\n")[:91]).encode("utf-8")
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

            print(f"SHA256SUMS: {sha256sums}")
            print(f"HASH: {hash}")

            if sha256sums != hash:
                request_selenium = True
                print("SHA256SUMS exists but does not matches current hash")
            else:
                print("SHA256SUMS exists and matches the current hash")

            file.close()
    else:
        print("SHA256SUMS does not exist")
        request_selenium = True

    if not os.path.isfile(BACKUP):
        print("BACKUP does not exist")
        request_selenium = True

    print("Requesting dynamic page source from selenium") if request_selenium else print("Opening backup page source")
    page_source = get_dynamic_page_source(hash) if request_selenium else get_backup_page_source()

    return page_source


def main():
    print("Getting page source from suitable mechanism")
    page_source = get_page_source()
    soup = BeautifulSoup(page_source, "lxml")

    return 0


if __name__ == "__main__":
    sys.exit(main())
