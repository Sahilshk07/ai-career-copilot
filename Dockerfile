FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/app.py

# Set work directory
WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (no .env — secrets come from Cloud Run env vars)
COPY backend /app/backend
COPY frontend /app/frontend

# Create writable directories in /tmp (Cloud Run filesystem is read-only except /tmp)
RUN mkdir -p /tmp/uploads /tmp/instance

# Expose port (Cloud Run injects PORT env var automatically)
EXPOSE 8080

# Start with gunicorn for production
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --threads 4 backend.app:app
