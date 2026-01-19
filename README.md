# Uma Musume Scout Scraper

A Python web scraper that extracts scout event information from the Uma Musume game website.

## Description

This project uses Selenium to scrape scout banner information from the Uma Musume webview, including titles, dates, and images. The scraped data is saved to `info.json` for easy access.

## Features

- Automated scraping of scout events
- Headless Chrome browser operation
- JSON output with timestamps
- Docker containerization for easy deployment
- Cron-based automation with git integration

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd scraper
   ```

2. Build the Docker image:
   ```bash
   docker compose build
   ```

## Usage

Run the scraper manually with Docker:
```bash
docker compose run scraper
```

The scraper will:
- Launch a headless Chrome browser
- Navigate to the Uma Musume info page
- Extract scout event details
- Save the data to `info.json`

For local development without Docker:
```bash
pip install -r requirements.txt
python scraper.py
```

## Dependencies

- beautifulsoup4==4.14.3
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
  "events": [
    {
      "title": "Event Title",
      "date": "Event Date",
      "image": "Image URL"
    }
  ],
  "timestamp": "2023-12-01 12:00:00"
}
```

## Automation

This project includes a cron script (`cronners.sh`) for automated runs. It rebuilds the Docker image, runs the scraper, and commits/pushes changes to git if any data has changed.

To set up cron automation:
1. Ensure SSH key is configured for git pushes.
2. Add to crontab (e.g., every 3 days):
   ```bash
   0 0 */3 * * /path/to/scraper/cronners.sh
   ```
3. Check logs in `/var/log/cronners_script.log`.
