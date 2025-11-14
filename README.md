# UT Registration Checker

A Python script that monitors UT Austin course registration status and alerts you when courses open up.

## Features

- Opens a browser for you to login manually
- Automatically detects when login is complete
- Monitors two course pages simultaneously
- Checks status every 5 minutes
- Alerts when status changes from "closed" to "open" or "waitlist"

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

Run the script:
```bash
python3.11 registration_checker.py
```

Or if you have Python 3.11 set as your default:
```bash
python registration_checker.py
```

The script will:
1. Open a browser window
2. Navigate to the first course page
3. **Wait for you to login manually** (you'll see the login page)
4. Once you login, it automatically detects and continues
5. Opens the second course page (you're already logged in)
6. Starts monitoring both courses every 5 minutes
7. Alerts you when any course status changes from "closed"

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

