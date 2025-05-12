# Novaxa Bot - Phase 2: CRM & Smart Reply

This repository contains the Python code for the Novaxa Bot, enhanced with a Customer Relationship Management (CRM) module and a Smart Reply Engine. The bot is designed to be managed via Telegram and a web-based dashboard.

## Project Structure

```
/home/ubuntu/workspace/novaxa_bot/
├── crm/
│   └── crm_module.py         # CRM logic
├── data/
│   ├── customers.json        # CRM data (example, should be managed securely)
│   ├── triggers.json         # Smart Reply triggers
│   ├── responses.json        # Smart Reply responses
│   └── mappings.json         # Smart Reply trigger-response mappings
├── smart_reply/
│   └── smart_reply_engine.py # Smart Reply logic
├── static/
│   └── style.css             # CSS for web dashboard
├── templates/
│   ├── dashboard.html        # Web dashboard main page
│   └── login.html            # Web dashboard login page
├── enhanced_bot.py           # Main bot application (Telegram bot & Flask dashboard)
├── requirements.txt          # Python dependencies
├── test_modules.py           # Unit tests (to be further developed)
├── .env                      # Local environment variables (DO NOT COMMIT ACTUAL VALUES)
├── .env.example              # Example environment variables
└── README.md                 # This file
```

## Features

*   **Telegram Bot Interface:**
    *   Standard commands: `/start`, `/help`, `/status`, `/id`.
    *   CRM commands: `/addcustomer`, `/findcustomer`, `/updatestatus`, `/addnote`.
    *   Smart Reply: Automatically responds to user messages based on predefined triggers and responses.
*   **CRM Module:**
    *   Manages customer data (name, email, Telegram ID, status, project associations, notes).
    *   Stores data in JSON files (for this version).
*   **Smart Reply Engine:**
    *   Manages triggers (keywords/phrases), responses, and mappings.
    *   Supports exact, contains, and regex matching for triggers.
    *   Can use CRM data to personalize responses (e.g., `Hello {crm_name}`).
*   **Web Dashboard (Flask):**
    *   Login protected.
    *   Displays bot status, CRM statistics (customer count), and Smart Reply statistics (trigger, response, mapping counts).
    *   (Further development can add management interfaces for CRM and Smart Reply data).

## Setup and Running

**1. Clone the Repository (if applicable):**
   If you are setting this up on a new machine:
   ```bash
   git clone https://github.com/1bidprice/novaxa_bot.git
   cd novaxa_bot
   ```

**2. Create a Virtual Environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

**3. Install Dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

**4. Configure Environment Variables:**
   *   Copy `.env.example` to a new file named `.env`:
     ```bash
     cp .env.example .env
     ```
   *   **Edit the `.env` file** with your actual credentials:
     *   `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token from BotFather.
     *   `TELEGRAM_ADMIN_IDS`: Your Telegram User ID (and other admin IDs, comma-separated). You can get your ID by sending `/id` to the bot once it's running with a temporary admin ID or by using another bot like `@userinfobot`.
     *   `FLASK_SECRET_KEY`: A long, random string for Flask session security.
     *   `DASHBOARD_USERNAME`: Username for the web dashboard.
     *   `DASHBOARD_PASSWORD`: Password for the web dashboard.

**5. Run the Bot:**
   ```bash
   python3 enhanced_bot.py
   ```
   The bot will start polling for Telegram messages, and the Flask web dashboard will be accessible (usually on `http://0.0.0.0:5000` or a port specified by your environment if deploying, e.g., Render).

## Using the Bot (Telegram)

*   Interact with your bot on Telegram.
*   Use `/help` to see available commands.
*   **CRM Commands (Examples):**
    *   `/addcustomer John Doe; john@example.com; 123456789; Lead; BidPrice Project; First contact via web.`
    *   `/findcustomer 123456789`
    *   `/updatestatus 123456789 Active Client`
    *   `/addnote 123456789 Followed up with a call.`
*   **Smart Replies:** Send messages that match your configured triggers.

## Accessing the Web Dashboard

1.  Open your web browser.
2.  Navigate to the address where the Flask app is running (e.g., `http://localhost:5000` if running locally, or the URL provided by your hosting service like Render).
3.  Log in with the `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD` you set in the `.env` file.

## Important Notes for Mobile Users (GitHub Management)

*   **Viewing Files:** GitHub's mobile interface allows viewing most text-based files, including `.py`, `.md`, `.json`, and `.txt`.
*   **Editing Files:** Simple edits to text files can often be done directly in the GitHub mobile web interface.
*   **Environment Variables (`.env`):** **NEVER** commit your actual `.env` file with real secrets to GitHub. The `.gitignore` file is set up to prevent this. When deploying to services like Render, you will set these environment variables directly in the Render dashboard, not by uploading the `.env` file.
*   **Folder Structure:** The current folder structure is designed for clarity. You can navigate it on GitHub mobile.

## Further Development / To-Do (from todo.md)

*   Complete unit tests for CRM and Smart Reply functionalities (`test_modules.py`).
*   Perform comprehensive integration testing of all components.
*   Develop more advanced backend logic for the web dashboard to manage CRM and Smart Reply data directly.
*   Implement more sophisticated error handling and logging.
*   Consider database solutions for CRM and Smart Reply data for scalability instead of JSON files.

This README provides a basic guide. For more detailed technical design, refer to the `Phase1_Technical_Plan.md` document (if available in the repository or provided separately).
