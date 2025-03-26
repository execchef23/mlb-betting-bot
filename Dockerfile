# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system tools
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code into container
COPY . .

# Setup CRON job
COPY cronjob.txt /etc/cron.d/mlb-cronjob
RUN chmod 0644 /etc/cron.d/mlb-cronjob && crontab /etc/cron.d/mlb-cronjob

# Create log file
RUN touch /app/data/cron.log

# Start cron + Streamlit
CMD ["sh", "-c", "cron && streamlit run dashboard.py --server.port=10000 --server.enableCORS=false"]