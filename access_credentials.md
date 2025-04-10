# NOVAXA Access Credentials

This document contains all the access credentials and information needed to manage your NOVAXA Telegram bot and web dashboard.

## Render Access

To access your deployed services on Render:

1. Visit the Render Dashboard: https://dashboard.render.com/
2. Log in with your Render account credentials
3. You will see your two services:
   - `novaxa-telegram-bot`
   - `novaxa-dashboard`

## Service URLs

Once deployed, your services will be available at:

- Telegram Bot API: https://novaxa-telegram-bot.onrender.com
- Web Dashboard: https://novaxa-dashboard.onrender.com

## Environment Variables

The following environment variables are configured on Render:

- `BOT_TOKEN`: 7658672268:AAHbvuM4fxYr2kiA-Aiynjgm5VPVTiYXe8U
- `DEBUG`: False
- `API_URL`: https://novaxa-telegram-bot.onrender.com/api (for the dashboard service)

## Updating Bot Token

To update your bot token:

1. Go to the Render Dashboard
2. Select the service you want to update
3. Go to the "Environment" tab
4. Find the `BOT_TOKEN` variable
5. Click "Edit" and enter the new token
6. Click "Save Changes"

Both services will automatically restart with the new token.

## Monitoring Access

If you set up monitoring with UptimeRobot or Better Stack as recommended:

### UptimeRobot
- Dashboard: https://uptimerobot.com/dashboard
- Username: Your email address
- Password: Your chosen password

### Better Stack (formerly Logtail)
- Dashboard: https://betterstack.com/logs
- Username: Your email address
- Password: Your chosen password

## Telegram Bot

Your Telegram bot is accessible at:

- Username: @NOVAXA_Bot (or the username you chose when creating the bot)
- Token: 7658672268:AAHbvuM4fxYr2kiA-Aiynjgm5VPVTiYXe8U

To interact with your bot:
1. Open Telegram
2. Search for your bot username
3. Start a conversation with the bot

## Security Notes

1. Keep this document secure as it contains sensitive information
2. Consider changing your bot token periodically for enhanced security
3. Use strong passwords for all associated accounts
4. Enable two-factor authentication where available

## Support

If you encounter any issues with your deployment:

1. Check the logs in your Render Dashboard
2. Run the test_deployment.py script to diagnose problems
3. Consult the documentation provided in the project files
