FROM python:3.12-slim-bookworm

# Debian's live repo only serves Chromium 150 now, which SIGTRAPs in this
# environment. Pin apt to a snapshot.debian.org timestamp from when an older,
# working Chromium was current. Bump SNAPSHOT to move the Chromium version;
# chromium + chromium-driver share a source package so they stay matched.
ARG SNAPSHOT=20240701T000000Z
RUN rm -f /etc/apt/sources.list.d/debian.sources && \
    printf 'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/%s bookworm main\ndeb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/%s bookworm-security main\n' "$SNAPSHOT" "$SNAPSHOT" > /etc/apt/sources.list

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium and ChromeDriver (pinned to the snapshot above)
RUN apt-get update && apt-get install -y chromium chromium-driver && \
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
