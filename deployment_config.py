"""
Deployment configuration for NOVAXA Dashboard and Telegram Bot
"""

import os
import json

# Configuration for different environments
config = {
    "development": {
        "api_url": "http://localhost:5000/api",
        "web_url": "http://localhost:8080",
        "debug": True,
        "webhook_enabled": False
    },
    "production": {
        "api_url": "https://api.novaxa-dashboard.example.com/api",
        "web_url": "https://novaxa-dashboard.example.com",
        "debug": False,
        "webhook_enabled": True,
        "webhook_url": "https://api.novaxa-dashboard.example.com/webhook"
    }
}

# Dockerfile for API
dockerfile_api = """
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .
COPY .env .

EXPOSE 5000

CMD ["python", "api.py"]
"""

# Dockerfile for Web
dockerfile_web = """
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY integration.py .
COPY templates/ templates/
COPY static/ static/
COPY .env .

EXPOSE 8080

CMD ["python", "integration.py"]
"""

# Docker Compose file
docker_compose = """
version: '3'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "5000:5000"
    environment:
      - ENVIRONMENT=production
    restart: always
    volumes:
      - api_data:/app/data

  web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=production
      - API_URL=http://api:5000/api
    depends_on:
      - api
    restart: always

volumes:
  api_data:
"""

# Nginx configuration for production
nginx_conf = """
server {
    listen 80;
    server_name novaxa-dashboard.example.com;
    
    location / {
        proxy_pass http://web:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://api:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /webhook {
        proxy_pass http://api:5000/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

# Requirements file
requirements = """
flask>=2.0.0
requests>=2.28.0
pyTelegramBotAPI>=4.10.0
schedule>=1.1.0
python-dotenv>=0.20.0
gunicorn>=20.1.0
"""

# Environment variables template
env_template = """
# Environment variables for NOVAXA Dashboard and Bot
ENVIRONMENT=development
BOT_TOKEN=7658672268:AAEHvAKeT9LT5jhkwL2ygMpt1SMzztnSZOM
API_URL=http://localhost:5000/api
WEB_URL=http://localhost:8080
DEBUG=True
WEBHOOK_ENABLED=False
WEBHOOK_URL=
"""

# Create deployment files
def create_deployment_files():
    """Create all necessary deployment files"""
    # Create directories if they don't exist
    os.makedirs("deployment", exist_ok=True)
    
    # Write Dockerfiles
    with open("deployment/Dockerfile.api", "w") as f:
        f.write(dockerfile_api)
    
    with open("deployment/Dockerfile.web", "w") as f:
        f.write(dockerfile_web)
    
    # Write Docker Compose file
    with open("deployment/docker-compose.yml", "w") as f:
        f.write(docker_compose)
    
    # Write Nginx configuration
    with open("deployment/nginx.conf", "w") as f:
        f.write(nginx_conf)
    
    # Write requirements file
    with open("deployment/requirements.txt", "w") as f:
        f.write(requirements)
    
    # Write environment variables template
    with open("deployment/.env.template", "w") as f:
        f.write(env_template)
    
    # Write configuration file
    with open("deployment/config.json", "w") as f:
        json.dump(config, f, indent=4)
    
    print("Deployment files created successfully!")

if __name__ == "__main__":
    create_deployment_files()
