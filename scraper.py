import json
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import schedule

def scrape_info():
    url = "https://webview.games.umamusume.com/umamusume/contents/v/index.html#/info?p=1&c=0"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=options)
    driver.get(url)
    print("Waiting 10 seconds for JS to load")
    time.sleep(10)  # Allow JS to load
    print(f"Page title: {driver.title}")

    scouts = []
    processed_titles = set()
    while True:
        lis = driver.find_elements(By.TAG_NAME, 'li')
        print(f"Found {len(lis)} <li> elements")
        found = False
        for i, li in enumerate(lis):
            try:
                class_attr = li.get_attribute('class')
                text = li.text
                print(f"LI {i}: class='{class_attr}' text='{text}'")
                if 'type-111' in class_attr:  # Scout type
                    print(f"Found type-111 li {i}")
                    if text not in processed_titles:
                        print("Processing")
                        title = text
                        processed_titles.add(title)
                        try:
                            img = li.find_element(By.TAG_NAME, 'img')
                            image_src = img.get_attribute('src')
                        except:
                            image_src = ""
                        a = li.find_element(By.TAG_NAME, 'a')
                        a.click()
                        print(f"Clicked, URL: {driver.current_url}")
                        time.sleep(5)
                        body_text = driver.find_element(By.TAG_NAME, 'body').text
                        print("Page text after click:")
                        print(body_text)
                        dates = re.findall(r'.*\(UTC\).*', body_text)
                        dates = [d.strip() for d in dates]
                        if len(dates) > 3:
                            date = dates[3]
                        else:
                            date = ""
                        scouts.append({"title": title, "date": date, "image": image_src})
                        driver.back()
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'li')))
                        found = True
                        break
                    else:
                        print("Already processed")
            except:
                print(f"Error with LI {i}, skipping")
                continue
        if not found:
            break

    driver.quit()

    # Save to JSON
    data = {"url": url, "scouts": scouts, "timestamp": time.time()}
    with open('info.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Scout data scraped and saved to info.json")

# Run once
scrape_info()
