# Render Deployment Guide for NOVAXA Telegram Bot

This document provides step-by-step instructions for deploying the NOVAXA Telegram Bot to Render.

## Prerequisites

Before deploying to Render, ensure you have:

1. A Render account (sign up at https://render.com if you don't have one)
2. The NOVAXA bot code with environment variable support
3. The bot token from BotFather

## Deployment Steps

### 1. Create a New Web Service on Render

1. Log in to your Render account
2. Click on "New +" button in the dashboard
3. Select "Web Service"
4. Connect your GitHub/GitLab repository or use the "Upload Files" option
   - If using GitHub/GitLab, connect your repository containing the NOVAXA bot code
   - If using "Upload Files", upload the zip file containing the NOVAXA bot code

### 2. Configure the Web Service

Fill in the following details:

- **Name**: `novaxa-telegram-bot`
- **Environment**: `Python 3`
- **Region**: Choose the region closest to you (e.g., Frankfurt for Europe)
- **Branch**: `main` (or your default branch)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `bash render_start.sh`

### 3. Add Environment Variables

Click on "Advanced" and then "Add Environment Variable" to add the following:

- `BOT_TOKEN = os.getenv("BOT_TOKEN")`
- `WEBHOOK_ENABLED`: `False`
- `DEBUG`: `False`
- `PORT`: `10000`

### 4. Set Resource Configuration

- **Instance Type**: Free (for testing) or Basic (for production)
- **Auto-Deploy**: Enable

### 5. Create Web Service

Click on "Create Web Service" to start the deployment process.

## Monitoring the Deployment

1. Render will automatically build and deploy your application
2. You can monitor the build and deployment process in the "Logs" tab
3. Once deployment is complete, Render will provide a URL for your service (e.g., `https://novaxa-telegram-bot.onrender.com`)

## Verifying the Deployment

To verify that your bot is running correctly:

1. Visit the provided URL in your browser
2. You should see a message indicating that the NOVAXA Bot is running
3. Send a message to your bot on Telegram to test its functionality

## Troubleshooting

If you encounter any issues:

1. Check the "Logs" tab in Render for error messages
2. Ensure all environment variables are set correctly
3. Verify that the `render_start.sh` script is executable
4. Check that the requirements.txt file includes all necessary dependencies

## Updating the Bot Token

If you need to update the bot token in the future:

1. Go to the "Environment" tab in your Render dashboard
2. Find the `BOT_TOKEN` variable
3. Click "Edit" and update the value
4. Save the changes
5. Render will automatically redeploy your application with the new token

This is the "safety valve" mechanism you requested, allowing you to change the token in one place without modifying the code.
