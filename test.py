import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def test_scrape():
    url = "https://webview.games.umamusume.com/umamusume/contents/v/index.html#/info?p=1&c=0"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.get(url)
    print("Waiting 15 seconds for JS to load")
    time.sleep(15)  # Allow JS to load
    print(f"Page title: {driver.title}")

    # Print the entire HTML
    html = driver.page_source
    print("Full HTML:")
    print(html)

    driver.quit()


if __name__ == "__main__":
    test_scrape()
