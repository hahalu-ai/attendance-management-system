FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy backend requirements first for better caching
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./backend/

# Copy frontend files
COPY frontend/ ./frontend/

# Set working directory to backend
WORKDIR /app/backend

# Expose port (Railway will provide this via $PORT)
EXPOSE 5001

# Start command - gunicorn will look for run:app in current directory
CMD gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
