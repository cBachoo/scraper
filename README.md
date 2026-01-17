# Uma Musume Scout Scraper

<<<<<<< HEAD
A Python web scraper that extracts scout event information from the Uma Musume game website.

## Description

This project uses Selenium to scrape scout banner information from the Uma Musume webview, including titles, dates, and images. The scraped data is saved to `info.json` for easy access.
=======
A Python web scraper that extracts scout event information from the Umamusume game website.

## Description

This project uses Selenium to scrape scout banner information from the Umamusume webview, including titles, dates, and images. The scraped data is saved to `info.json` for easy access.
>>>>>>> 62f4382ea3f9f76917c27c4c6a1380f7eefcac3d

## Features

- Automated scraping of scout events
- Headless Chrome browser operation
- JSON output with timestamps
- Scheduled runs via GitHub Actions (every 3 days)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the scraper manually:
```bash
python scraper.py
```

The scraper will:
- Launch a headless Chrome browser
- Navigate to the Uma Musume info page
- Extract scout event details
- Save the data to `info.json`

## Dependencies

- beautifulsoup4==4.14.3
- schedule==1.2.2
- selenium==4.39.0
- webdriver_manager==4.0.2

## Output

The scraped data is stored in `info.json` with the following structure:
```json
{
  "url": "https://webview.games.umamusume.com/...",
  "scouts": [
    {
      "title": "Event Title",
      "date": "Event Date",
      "image": "Image URL"
    }
  ],
  "timestamp": 1234567890.123
}
```

## Automation

<<<<<<< HEAD
This project includes a GitHub Actions workflow that automatically runs the scraper every 3 days and commits any new data to the repository.
=======
This project includes a GitHub Actions workflow that automatically runs the scraper every 3 days and commits any new data to the repository.
>>>>>>> 62f4382ea3f9f76917c27c4c6a1380f7eefcac3d
