# NOVAXA Continuous Deployment Configuration

This file contains the configuration for continuous deployment and monitoring of the NOVAXA Telegram bot and web dashboard on Render.

## Continuous Deployment

Render provides built-in continuous deployment from Git repositories. When you connect your repository to Render, it will automatically deploy your application whenever you push changes to the connected branch.

### For Telegram Bot

1. Create a new Web Service on Render
2. Connect to your Git repository
3. Configure the following settings:
   - **Name**: `novaxa-telegram-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `bash render_start.sh`
   - **Auto-Deploy**: Enabled

### For Web Dashboard

1. Create a new Web Service on Render
2. Connect to your Git repository
3. Configure the following settings:
   - **Name**: `novaxa-dashboard`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `bash start_dashboard.sh`
   - **Auto-Deploy**: Enabled

## Environment Variables

Both services require the following environment variables:

- `BOT_TOKEN`: Your Telegram bot token (7658672268:AAHbvuM4fxYr2kiA-Aiynjgm5VPVTiYXe8U)
- `DEBUG`: Set to "False" for production
- `API_URL`: For the dashboard, set to the URL of your bot API (e.g., https://novaxa-telegram-bot.onrender.com/api)

## Monitoring

Render provides built-in monitoring for your services. You can view logs, metrics, and set up alerts.

### Health Checks

Both the bot and dashboard include health check endpoints:

- Bot: `/health`
- Dashboard: `/health`

You can configure Render to monitor these endpoints to ensure your services are running properly.

### Custom Monitoring

For more advanced monitoring, you can use the following:

1. **Uptime Robot**: Free service that checks your endpoints every 5 minutes
   - Create an account at https://uptimerobot.com
   - Add monitors for both your bot and dashboard URLs
   - Set up email alerts for downtime

2. **Better Stack (formerly Logtail)**: Monitoring and logging service
   - Create an account at https://betterstack.com
   - Add your Render services as monitors
   - Configure alerts via email, SMS, or other channels

## Keeping Services Active

Render's free tier will spin down services after periods of inactivity. To prevent this:

1. **For the Telegram Bot**:
   - The `render_start.sh` script includes a keep-alive mechanism
   - The bot's polling mechanism keeps the service active

2. **For the Web Dashboard**:
   - The `integration.py` file includes a health check thread that runs every 5 minutes
   - You can use an external service like UptimeRobot to ping your dashboard regularly

## Updating the Bot Token

When you need to update the bot token:

1. Go to your Render dashboard
2. Select the service (bot or dashboard)
3. Go to the "Environment" tab
4. Update the `BOT_TOKEN` variable
5. Click "Save Changes"

Render will automatically restart your service with the new token.

## Troubleshooting

If your services go down or experience issues:

1. Check the Render logs for error messages
2. Verify that all environment variables are set correctly
3. Ensure your services haven't exceeded Render's free tier limits
4. Check if your bot token is still valid

For persistent issues, you may need to manually restart the services from the Render dashboard.
