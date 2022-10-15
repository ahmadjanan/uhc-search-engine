# UHC Search Engine
___
A Flask-based search engine which allows a user to search for UHC plans and corresponding file URLs provided on https://transparency-in-coverage.uhc.com.

It has three modules
1. Scraper - Scrapes JSON files' URLs from UHC website.
2. JSON Downloader - Downloads, formats and merges all the JSON files.
3. Flask Application - A search engine to query the centralized JSON files database.


# Table of contents
___
1. [Requirements](README.md#1-requirements)
2. [Directory Structure](README.md#2-directory-structure)
3. [Setup Project](README.md#3-setup-project)

# 1. Requirements
___
1. Python 3.9.x
2. ChromeDriver 106.0.5249.61+  (https://chromedriver.chromium.org/getting-started)


# 2. Directory Structure
___
Clone the repository.
```
    git clone https://github.com/ahmadjanan/uhc-search-engine.git
```

# 3. Setup Project
___
- Install requirements
    ```
    pip install -r requirements.txt
    ```
- Scrape and extract JSON URLs from webite.
    ```
    python scraper.py  
    ```
- Download JSON files and populate backend database.
    ```
    python json_downloader.py
    ```
- Run server.
    ```
    python server.py  
    ```
