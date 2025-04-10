"""
Deployment script for NOVAXA Dashboard and Telegram Bot
"""

import os
import subprocess
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_prerequisites():
    """Check if all prerequisites are installed"""
    logger.info("Checking prerequisites...")
    
    # Check if Docker is installed
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        logger.info("✅ Docker is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ Docker is not installed. Please install Docker first.")
        return False
    
    # Check if Docker Compose is installed
    try:
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        logger.info("✅ Docker Compose is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("❌ Docker Compose is not installed. Please install Docker Compose first.")
        return False
    
    return True

def prepare_deployment_files():
    """Prepare deployment files"""
    logger.info("Preparing deployment files...")
    
    # Check if deployment directory exists
    if not os.path.exists("deployment"):
        logger.error("❌ Deployment directory not found. Please run deployment_config.py first.")
        return False
    
    # Check if all required files exist
    required_files = [
        "Dockerfile.api",
        "Dockerfile.web",
        "docker-compose.yml",
        "nginx.conf",
        "requirements.txt",
        ".env.template"
    ]
    
    for file in required_files:
        if not os.path.exists(os.path.join("deployment", file)):
            logger.error(f"❌ Required file {file} not found in deployment directory.")
            return False
    
    logger.info("✅ All deployment files are present")
    
    # Create .env file from template if it doesn't exist
    env_file = os.path.join("deployment", ".env")
    if not os.path.exists(env_file):
        with open(os.path.join("deployment", ".env.template"), "r") as template:
            with open(env_file, "w") as env:
                env.write(template.read())
        logger.info("✅ Created .env file from template")
    
    return True

def copy_application_files():
    """Copy application files to deployment directory"""
    logger.info("Copying application files to deployment directory...")
    
    # Create directories if they don't exist
    os.makedirs(os.path.join("deployment", "templates"), exist_ok=True)
    os.makedirs(os.path.join("deployment", "static"), exist_ok=True)
    os.makedirs(os.path.join("deployment", "static", "css"), exist_ok=True)
    os.makedirs(os.path.join("deployment", "static", "js"), exist_ok=True)
    os.makedirs(os.path.join("deployment", "static", "img"), exist_ok=True)
    
    # Copy API file
    try:
        with open("api.py", "r") as src:
            with open(os.path.join("deployment", "api.py"), "w") as dst:
                dst.write(src.read())
        logger.info("✅ Copied api.py")
    except FileNotFoundError:
        logger.error("❌ api.py not found")
        return False
    
    # Copy integration file
    try:
        with open("integration.py", "r") as src:
            with open(os.path.join("deployment", "integration.py"), "w") as dst:
                dst.write(src.read())
        logger.info("✅ Copied integration.py")
    except FileNotFoundError:
        logger.error("❌ integration.py not found")
        return False
    
    # Copy HTML files
    try:
        with open("index.html", "r") as src:
            with open(os.path.join("deployment", "templates", "index.html"), "w") as dst:
                dst.write(src.read())
        logger.info("✅ Copied index.html")
    except FileNotFoundError:
        logger.error("❌ index.html not found")
        return False
    
    # Copy CSS files
    try:
        with open(os.path.join("css", "styles.css"), "r") as src:
            with open(os.path.join("deployment", "static", "css", "styles.css"), "w") as dst:
                dst.write(src.read())
        logger.info("✅ Copied styles.css")
    except FileNotFoundError:
        logger.error("❌ styles.css not found")
        return False
    
    # Copy JS files
    try:
        with open(os.path.join("js", "main.js"), "r") as src:
            with open(os.path.join("deployment", "static", "js", "main.js"), "w") as dst:
                dst.write(src.read())
        logger.info("✅ Copied main.js")
    except FileNotFoundError:
        logger.error("❌ main.js not found")
        return False
    
    return True

def build_docker_images():
    """Build Docker images"""
    logger.info("Building Docker images...")
    
    # Change to deployment directory
    os.chdir("deployment")
    
    # Build API image
    try:
        subprocess.run(["docker", "build", "-t", "novaxa-api", "-f", "Dockerfile.api", "."], check=True)
        logger.info("✅ Built novaxa-api Docker image")
    except subprocess.CalledProcessError:
        logger.error("❌ Failed to build novaxa-api Docker image")
        return False
    
    # Build Web image
    try:
        subprocess.run(["docker", "build", "-t", "novaxa-web", "-f", "Dockerfile.web", "."], check=True)
        logger.info("✅ Built novaxa-web Docker image")
    except subprocess.CalledProcessError:
        logger.error("❌ Failed to build novaxa-web Docker image")
        return False
    
    return True

def deploy_with_docker_compose():
    """Deploy with Docker Compose"""
    logger.info("Deploying with Docker Compose...")
    
    # Make sure we're in the deployment directory
    if not os.path.exists("docker-compose.yml"):
        os.chdir("deployment")
    
    # Stop any running containers
    try:
        subprocess.run(["docker-compose", "down"], check=True)
        logger.info("✅ Stopped any running containers")
    except subprocess.CalledProcessError:
        logger.warning("⚠️ Failed to stop running containers, continuing anyway")
    
    # Start containers
    try:
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        logger.info("✅ Started containers with Docker Compose")
    except subprocess.CalledProcessError:
        logger.error("❌ Failed to start containers with Docker Compose")
        return False
    
    return True

def verify_deployment():
    """Verify deployment is working"""
    logger.info("Verifying deployment...")
    
    # Wait for services to start
    logger.info("Waiting for services to start...")
    time.sleep(10)
    
    # Check if API is running
    try:
        result = subprocess.run(["docker-compose", "ps", "api"], capture_output=True, text=True, check=True)
        if "Up" in result.stdout:
            logger.info("✅ API service is running")
        else:
            logger.error("❌ API service is not running")
            return False
    except subprocess.CalledProcessError:
        logger.error("❌ Failed to check API service status")
        return False
    
    # Check if Web is running
    try:
        result = subprocess.run(["docker-compose", "ps", "web"], capture_output=True, text=True, check=True)
        if "Up" in result.stdout:
            logger.info("✅ Web service is running")
        else:
            logger.error("❌ Web service is not running")
            return False
    except subprocess.CalledProcessError:
        logger.error("❌ Failed to check Web service status")
        return False
    
    logger.info("✅ Deployment verified successfully!")
    return True

def deploy():
    """Main deployment function"""
    logger.info("Starting deployment of NOVAXA Dashboard and Telegram Bot...")
    
    # Check prerequisites
    if not check_prerequisites():
        return False
    
    # Prepare deployment files
    if not prepare_deployment_files():
        return False
    
    # Copy application files
    if not copy_application_files():
        return False
    
    # Build Docker images
    if not build_docker_images():
        return False
    
    # Deploy with Docker Compose
    if not deploy_with_docker_compose():
        return False
    
    # Verify deployment
    if not verify_deployment():
        return False
    
    logger.info("🎉 Deployment completed successfully!")
    logger.info("You can access the dashboard at: http://localhost:8080")
    logger.info("API is available at: http://localhost:5000/api")
    
    return True

if __name__ == "__main__":
    success = deploy()
    if not success:
        logger.error("Deployment failed!")
        sys.exit(1)
