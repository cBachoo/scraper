import json
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def scrape_info():
    url = "https://webview.games.umamusume.com/umamusume/contents/v/index.html#/info?p=1&c=0"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=options)
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

    scouts = []
    events = []

    # Collect all scout titles
    scout_titles = set()
    for li in lis:
        try:
            class_attr = li.get_attribute("class")
            text = li.text
            if class_attr and "type-111" in class_attr:
                scout_titles.add(text)
        except:
            continue

    # Collect all event titles
    event_titles = set()
    for li in lis:
        try:
            class_attr = li.get_attribute("class")
            text = li.text
            if class_attr and "type-104" in class_attr:
                event_titles.add(text)
        except:
            continue

    # Process scouts
    for title in scout_titles:
        print(f"Processing scout: {title}")
        # Refind lis to ensure validity
        lis = driver.find_elements(By.TAG_NAME, "li")
        for li in lis:
            if li.text == title:
                try:
                    img = li.find_element(By.TAG_NAME, "img")
                    image_src = img.get_attribute("src")
                except:
                    image_src = ""
                a = li.find_element(By.TAG_NAME, "a")
                a.click()
                print(f"Clicked scout, URL: {driver.current_url}")
                time.sleep(5)
                body_text = driver.find_element(By.TAG_NAME, "body").text
                dates = re.findall(r".*\(UTC\).*", body_text)
                dates = [d.strip() for d in dates]
                date = dates[3] if len(dates) > 3 else ""
                if date:
                    scouts.append({"title": title, "date": date, "image": image_src})
                driver.get(url)
                time.sleep(5)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "li"))
                )
                break

    # Process events
    for title in event_titles:
        print(f"Processing event: {title}")
        # Refind lis
        lis = driver.find_elements(By.TAG_NAME, "li")
        for li in lis:
            if li.text == title:
                try:
                    img = li.find_element(By.TAG_NAME, "img")
                    image_src = img.get_attribute("src")
                except:
                    image_src = ""
                a = li.find_element(By.TAG_NAME, "a")
                a.click()
                print(f"Clicked event, URL: {driver.current_url}")
                time.sleep(5)
                body_text = driver.find_element(By.TAG_NAME, "body").text
                dates = re.findall(r".*\(UTC\).*", body_text)
                dates = [d.strip() for d in dates]
                date = dates[3] if len(dates) > 3 else ""
                if date:
                    events.append({"title": title, "date": date, "image": image_src})
                driver.get(url)
                time.sleep(5)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "li"))
                )
                break

    driver.quit()

    # Save to JSON
    data = {"url": url, "scouts": scouts, "events": events, "timestamp": time.time()}
    with open("info.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Scout and event data scraped and saved to info.json")


# Run once
scrape_info()
