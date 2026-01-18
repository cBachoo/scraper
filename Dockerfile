FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium and ChromeDriver
RUN apt-get update && apt-get install -y chromium chromium-chromedriver && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the environment
COPY . .

# Run the scraper
CMD ["python", "scraper.py"]
