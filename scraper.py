import datetime
import json
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def get_titles(driver, class_name):
    """Collect unique titles for items with the given class."""
    lis = driver.find_elements(By.TAG_NAME, "li")
    titles = []
    for li in lis:
        try:
            class_attr = li.get_attribute("class")
            text = li.text
            if class_attr and class_name in class_attr and text not in titles:
                titles.append(text)
        except:
            continue
    return titles


def get_item_urls(driver, base_url, titles):
    """Collect (title, url) pairs by clicking each item and capturing the URL."""
    items = []
    for title in titles:
        try:
            lis = driver.find_elements(By.TAG_NAME, "li")
            for li in lis:
                if li.text == title:
                    a = li.find_element(By.TAG_NAME, "a")
                    a.click()
                    time.sleep(2)
                    item_url = driver.current_url
                    driver.get(base_url)
                    time.sleep(2)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "li"))
                    )
                    items.append((title, item_url))
                    break
        except Exception as e:
            print(f"Error processing {title}: {e}")
            continue
    return items


def extract_data_from_url(driver, title, item_url, item_type):
    """Extract data from a direct item URL."""
    print(f"Processing {item_type}: {title}")
    driver.get(item_url)
    time.sleep(5)
    body_text = driver.find_element(By.TAG_NAME, "body").text
    lines = body_text.split("\n")
    if item_type == "event" and "legend" in title.lower():
        # Special handling for legend events
        dates_list = [line.strip() for line in lines if "(UTC)" in line and "-" in line]
        imgs = driver.find_elements(By.TAG_NAME, "img")
        images_list = [
            img.get_attribute("src") for img in imgs if img.get_attribute("src")
        ]
        # Store all dates and images for testing/debugging
        print(f"Legend: using {len(dates_list)} dates, {len(images_list)} images")
        return {
            "title": title,
            "legend": {"dates": dates_list, "images": images_list},
        }
    else:
        return None  # temporary stop handling non-legend events for debugging
        # Normal handling for scouts and non-legend events
        dates = [line for line in lines if "(UTC)" in line and "-" in line]
        date = dates[0].strip() if dates else ""
        imgs = driver.find_elements(By.TAG_NAME, "img")
        image_src = imgs[0].get_attribute("src") if imgs else ""
        if date:
            return {"title": title, "date": date, "image": image_src}
        else:
            return None


def scrape_items(driver, items, item_type):
    """Scrape data for all items."""
    scraped = []
    for title, url in items:
        data = extract_data_from_url(driver, title, url, item_type)
        if data:
            scraped.append(data)
    return scraped


def scrape_info():
    url = "https://webview.games.umamusume.com/umamusume/contents/v/index.html#/info?p=1&c=0"
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
    driver.get(url)
    print("Waiting 15 seconds for JS to load")
    time.sleep(15)  # Allow JS to load
    print(f"Page title: {driver.title}")

    # Initial check for sufficient elements
    lis = driver.find_elements(By.TAG_NAME, "li")
    print(f"Found {len(lis)} <li> elements")
    if len(lis) <= 3:
        print(
            "Error: Found only {} <li> elements, expected more than 3".format(len(lis))
        )
        driver.quit()
        raise SystemExit("Insufficient <li> elements")

    # Collect titles
    # scout_titles = get_titles(driver, "type-111")  # Commented out for debugging legend
    scout_titles = []
    event_titles = get_titles(driver, "type-104")
    # print(f"Found {len(scout_titles)} scouts (type-111)")  # Commented out
    print(f"Found {len(event_titles)} events (type-104)")

    # Collect item URLs
    # scout_items = get_item_urls(driver, url, scout_titles)  # Commented out
    scout_items = []
    event_items = get_item_urls(driver, url, event_titles)

    # Scrape data
    # scouts = scrape_items(driver, scout_items, "scout")  # Commented out
    scouts = []
    events = scrape_items(driver, event_items, "event")

    driver.quit()

    # Save to JSON
    data = {
        "url": url,
        "scouts": scouts,
        "events": events,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open("info.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Scout and event data scraped and saved to info.json")


# Run once
scrape_info()
