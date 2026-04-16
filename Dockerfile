# Dockerfile - Docker build instructions
# TechRent Pro - Equipment Rental Platform

# 1. Use an official slim Python base image
FROM python:3.13-slim

# 2. Set a working directory inside the container
WORKDIR /app

# 3. Copy requirements BEFORE the rest of the code (layer caching)
COPY requirements.txt .

# 4. Install Python dependencies (no cache to keep image small)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application source code
COPY . .

# 6. Expose the Flask port
EXPOSE 5000

# 7. Set environment variables (defaults - override via --env-file)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

# 8. Start the app
# Run with: docker run --rm -p 5000:5000 --env-file .env web
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
