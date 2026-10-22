FROM python:3.12-slim-bookworm

# Debian's current Chromium (150) self-aborts on this host's kernel, so we pin an
# exact, reproducible Chrome + chromedriver via Chrome for Testing instead. Bump
# CHROME_MILESTONE to change the version; LATEST_RELEASE resolves a valid patch.
ARG CHROME_MILESTONE=146

# Runtime libs + fonts for a Chromium-based browser. Installing Debian's
# `chromium` package is the reliable way to pull the full dependency closure for
# this distro; Selenium is pointed at the pinned Chrome below, not this binary.
RUN apt-get update && apt-get install -y \
    chromium \
    wget \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download the pinned Chrome for Testing + matching chromedriver.
RUN set -eux; \
    VERSION="$(wget -qO- "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_MILESTONE}")"; \
    base="https://storage.googleapis.com/chrome-for-testing-public/${VERSION}/linux64"; \
    wget -q "${base}/chrome-linux64.zip" -O /tmp/chrome.zip; \
    wget -q "${base}/chromedriver-linux64.zip" -O /tmp/chromedriver.zip; \
    unzip -q /tmp/chrome.zip -d /opt; \
    unzip -q /tmp/chromedriver.zip -d /opt; \
    ln -sf /opt/chrome-linux64/chrome /usr/local/bin/chrome; \
    ln -sf /opt/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
    rm -f /tmp/chrome.zip /tmp/chromedriver.zip; \
    /usr/local/bin/chrome --version; \
    /usr/local/bin/chromedriver --version

# Set working directory
WORKDIR /app

# Install uv and the locked Python dependencies (cached unless the lockfile changes)
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-cache

# Copy the environment
COPY . .

# Run the scraper with the project venv
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "scraper.py"]
