# UT Registration Checker

A Python script and web interface that monitors UT Austin course registration status and alerts you when courses open up.

## Features

- **Web Interface**: Clean, modern web UI to configure and monitor courses
- **Interactive Setup**: Enter semester and course codes through the interface
- **Automatic Monitoring**: Opens a browser for you to login manually
- **Smart Detection**: Automatically detects when login is complete
- **Multi-Course Support**: Monitor any number of courses simultaneously
- **Real-time Alerts**: Loud alarms and notifications when courses open
- **Auto-Registration Link**: Opens registration page automatically when a course opens

## Setup

**Important:** This script requires Python 3.11 or 3.12 (Python 3.13 is not yet supported by Playwright dependencies).

1. Install Python dependencies using Python 3.11:
```bash
python3.11 -m pip install -r requirements.txt
```

2. Install Playwright browsers (Firefox is recommended for macOS stability):
```bash
python3.11 -m playwright install firefox
```

Or if you prefer Chromium:
```bash
python3.11 -m playwright install chromium
```

## Usage

### Web Interface (Recommended)

1. Start the web server:
```bash
python3.11 app.py
```

2. Open your browser and navigate to:
```
http://localhost:3000
```

3. In the web interface:
   - Enter the semester code (e.g., `20262` for Spring 2026)
   - Add course codes (the number at the end of the URL, e.g., `56615`, `56605`)
   - Click "Save Configuration"
   - Click "Start Monitoring" to begin

### Command Line Interface

Run the script directly:
```bash
python3.11 registration_checker.py
```

The script will:
1. Prompt you for semester code and course codes
2. Open a browser window
3. Navigate to the first course page
4. **Wait for you to login manually** (you'll see the login page)
5. Once you login, it automatically detects and continues
6. Opens additional course pages in new tabs (you're already logged in)
7. Starts monitoring all courses every 5 minutes
8. Alerts you when any course status changes from "closed"

Press `Ctrl+C` to stop monitoring.

## Configuration

You can modify the following in `registration_checker.py`:

- `CHECK_INTERVAL_MINUTES`: How often to check (default: 5 minutes)
- `COURSE_URLS`: The course URLs to monitor

## How It Works

The script uses Playwright to:
- Open a browser in visible mode (so you can login)
- Detect when login is complete by checking for course page elements
- Reload both course pages every 5 minutes
- Extract the status text from the table (looks for `td[data-th="Status"]`)
- Compare current status with initial status and alert on changes

