FROM python:3.10

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy application files
COPY . .

# Copy crontab file to the correct location
COPY crontab.txt /etc/cron.d/flag_cron

# Set permissions and apply the crontab
RUN chmod 0644 /etc/cron.d/flag_cron
RUN crontab /etc/cron.d/flag_cron

# Start cron and run the app
CMD service cron start && python3 flag_api.py

