import datetime
import json
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Constants
BASE_URL = (
    "https://webview.games.umamusume.com/umamusume/contents/v/index.html#/info?p=1&c=0"
)
SCOUT_CLASS = "type-111"
EVENT_CLASS = "type-104"
JS_LOAD_WAIT = 15
PAGE_RENDER_WAIT = 5
NAVIGATE_BACK_WAIT = 2
TIMEOUT = 10


def setup_chrome_driver():
    """Configure and return a Chrome WebDriver instance."""
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)


def get_titles(driver, class_name):
    """Collect unique titles for items with the given class name."""
    lis = driver.find_elements(By.TAG_NAME, "li")
    titles = []
    for li in lis:
        try:
            class_attr = li.get_attribute("class")
            text = li.text
            if class_attr and class_name in class_attr and text not in titles:
                titles.append(text)
        except Exception:
            continue
    return titles


def get_page_text_and_images(driver):
    """Extract body text and image sources from current page."""
    body_text = driver.find_element(By.TAG_NAME, "body").text
    lines = body_text.split("\n")

    imgs = driver.find_elements(By.TAG_NAME, "img")
    images = [img.get_attribute("src") for img in imgs if img.get_attribute("src")]

    return lines, images


def extract_dates(lines):
    """Extract dates with time ranges containing (UTC) and dash."""
    return [line.strip() for line in lines if "(UTC)" in line and " - " in line]


def create_legend_pairs(dates_list, all_images):
    """Create date-image pairs for legend events, skipping the banner image."""
    # Skip the first image (banner) and match remaining images with dates
    character_images = all_images[1:] if len(all_images) > 1 else all_images

    # Create date-image pairs
    min_count = min(len(dates_list), len(character_images))
    return [
        {"date": dates_list[i], "image": character_images[i]} for i in range(min_count)
    ]


def extract_banner_id(image_url):
    """Extract the numeric banner ID from an image URL (e.g. 3068 from banner_3068_...)."""
    match = re.search(r"banner_(\d+)", image_url)
    return match.group(1) if match else None


def get_item_banner_ids(item):
    """Collect all banner IDs for an item, including nested legend race images."""
    banner_ids = set()
    image = item.get("image", "")
    if image:
        banner_id = extract_banner_id(image)
        if banner_id:
            banner_ids.add(banner_id)
    # Legend events store their images inside a "legend" list rather than at the top level
    for entry in item.get("legend", []):
        banner_id = extract_banner_id(entry.get("image", ""))
        if banner_id:
            banner_ids.add(banner_id)
    return banner_ids


def is_coming_soon(item):
    """Return True if the item's title marks it as an upcoming (not yet live) entry."""
    return "coming" in item.get("title", "").lower()


def deduplicate_items(items):
    """Remove 'coming soon' entries when a live version of the same banner exists."""
    # Collect banner IDs that already have a live (non-coming, e.g. "here") entry
    live_banners = set()
    for item in items:
        if not is_coming_soon(item):
            live_banners.update(get_item_banner_ids(item))

    result = []
    for item in items:
        if is_coming_soon(item):
            banner_ids = get_item_banner_ids(item)
            if banner_ids and banner_ids <= live_banners:
                print(
                    f"  Skipping duplicate (banners {sorted(banner_ids)}): "
                    f"{item['title'][:60]}"
                )
                continue
        result.append(item)
    return result


def extract_legend_data(driver, title):
    """Extract data for legend race events."""
    lines, all_images = get_page_text_and_images(driver)
    dates_list = extract_dates(lines)
    date_image_pairs = create_legend_pairs(dates_list, all_images)

    print(f"  Found {len(date_image_pairs)} legend race entries")

    return {"title": title, "legend": date_image_pairs}


_UMA_RE = re.compile(r"^[★☆]{1,3}\s+(.+)")
_SUPPORT_RE = re.compile(r"^[•・]\s*(SSR|SR|R)\s+(.+)")


def extract_featured_banners(lines):
    uma, supports, section = [], [], None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if "■" in line:
            lower = line.lower()
            section = (
                "uma" if "debut trainee umamusume" in lower
                else "support" if "debut support cards" in lower
                else None
            )
            continue
        if section == "uma" and (m := _UMA_RE.match(line)):
            name = m.group(1).strip()
            # Unique-skill flavor text is also bulleted with a star and can
            # follow the uma name line; it reads as a long sentence ending
            # in a period, unlike the short "[Title] Name" format.
            if name.endswith("."):
                continue
            uma.append(name)
        elif section == "support" and (m := _SUPPORT_RE.match(line)):
            supports.append({"rarity": m.group(1), "name": m.group(2).strip()})
    return uma, supports


def extract_standard_data(driver, title):
    """Extract data for standard scouts and events."""
    lines, images = get_page_text_and_images(driver)
    dates = extract_dates(lines)

    date = dates[0].strip() if dates else ""
    image = images[0] if images else ""

    if not date:
        return None

    result = {"title": title, "date": date, "image": image}

    uma, supports = extract_featured_banners(lines)
    if uma:
        result["featured_uma"] = uma
    if supports:
        result["featured_supports"] = supports

    return result


def extract_data_from_page(driver, title, item_type):
    """Extract data from the current page based on item type."""
    print(f"Processing {item_type}: {title}")

    if item_type == "event" and "legend" in title.lower():
        return extract_legend_data(driver, title)
    else:
        return extract_standard_data(driver, title)


def click_and_extract(driver, base_url, title, item_type):
    """Click on an item, extract its data, and navigate back."""
    lis = driver.find_elements(By.TAG_NAME, "li")
    for li in lis:
        if li.text == title:
            a = li.find_element(By.TAG_NAME, "a")
            a.click()
            time.sleep(PAGE_RENDER_WAIT)

            # Extract data immediately while we're on the page
            data = extract_data_from_page(driver, title, item_type)

            # Navigate back to list
            driver.get(base_url)
            time.sleep(NAVIGATE_BACK_WAIT)
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, "li"))
            )

            return data
    return None


def scrape_items_by_clicking(driver, base_url, titles, item_type):
    """Click each item and extract data immediately while on the page."""
    scraped = []
    for title in titles:
        try:
            data = click_and_extract(driver, base_url, title, item_type)
            if data:
                scraped.append(data)
        except Exception as e:
            print(f"Error processing {title}: {e}")
            continue
    return scraped


def validate_page_loaded(driver):
    """Check that sufficient page elements have loaded."""
    lis = driver.find_elements(By.TAG_NAME, "li")
    print(f"Found {len(lis)} <li> elements")
    if len(lis) <= 3:
        raise SystemExit(
            f"Error: Found only {len(lis)} <li> elements, expected more than 3"
        )


def save_to_json(data, filename="info.json"):
    """Save scraped data to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Scout and event data scraped and saved to {filename}")


def scrape_info():
    """Main scraping function."""
    driver = setup_chrome_driver()

    try:
        driver.get(BASE_URL)
        print(f"Waiting {JS_LOAD_WAIT} seconds for JS to load")
        time.sleep(JS_LOAD_WAIT)
        print(f"Page title: {driver.title}")

        # Validate page loaded correctly
        validate_page_loaded(driver)

        # Collect titles
        scout_titles = get_titles(driver, SCOUT_CLASS)
        event_titles = get_titles(driver, EVENT_CLASS)
        print(f"Found {len(scout_titles)} scouts ({SCOUT_CLASS})")
        print(f"Found {len(event_titles)} events ({EVENT_CLASS})")

        # Scrape data by clicking and extracting immediately
        scouts = deduplicate_items(
            scrape_items_by_clicking(driver, BASE_URL, scout_titles, "scout")
        )
        events = deduplicate_items(
            scrape_items_by_clicking(driver, BASE_URL, event_titles, "event")
        )

        # Prepare and save data
        data = {
            "url": BASE_URL,
            "scouts": scouts,
            "events": events,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_to_json(data)

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_info()
