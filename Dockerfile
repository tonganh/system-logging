FROM python:3.9-slim

# Install system dependencies
# iputils-ping is needed for the ping command in check_internet
RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY monitor.py .

# Create logs directory
RUN mkdir logs

CMD ["python", "monitor.py"]
