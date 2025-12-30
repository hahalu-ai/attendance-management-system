FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will provide this via $PORT)
EXPOSE 5001

# Start command
CMD gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
