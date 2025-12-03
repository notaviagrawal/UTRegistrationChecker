#!/usr/bin/env python3.11
"""
UT Registration Checker
Monitors course registration status and alerts when courses open up.
"""

import time
import os
import sys
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Base URL for course schedule
BASE_COURSE_URL = "https://utdirect.utexas.edu/apps/registrar/course_schedule"

# Registration page URL to open when a course opens
REGISTRATION_URL = "https://utdirect.utexas.edu/registration/registration.WBX"

# Check interval in minutes
CHECK_INTERVAL_MINUTES = 5
CHECK_INTERVAL_SECONDS = CHECK_INTERVAL_MINUTES * 60

# Selector for the status cell in the table
STATUS_SELECTOR = 'td[data-th="Status"]'

# Expected title when logged in (to detect successful login)
LOGGED_IN_TITLE = "UT Austin Registrar"


def log(message):
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_course_codes():
    """Interactively get course codes from the user."""
    print("\n" + "=" * 60)
    print("UT Registration Checker - Course Setup")
    print("=" * 60)
    
    # Get semester code
    print("\nEnter the semester code (e.g., 20262 for Spring 2026):")
    semester = input("Semester code: ").strip()
    
    if not semester:
        print("ERROR: Semester code is required. Exiting.")
        return None, []
    
    # Get course codes
    course_codes = []
    print(f"\nEnter course codes (the number at the end of the URL, e.g., 56615, 56605)")
    print("Press Enter with no input when done adding courses.\n")
    
    while True:
        course_code = input(f"Course code #{len(course_codes) + 1} (or press Enter to finish): ").strip()
        
        if not course_code:
            if len(course_codes) == 0:
                print("ERROR: You must enter at least one course code. Exiting.")
                return None, []
            break
        
        # Validate it's a number
        if not course_code.isdigit():
            print(f"WARNING: '{course_code}' is not a valid course code (should be numbers only). Skipping.")
            continue
        
        course_codes.append(course_code)
        print(f"✓ Added course code: {course_code}")
    
    print(f"\n✓ Setup complete: {len(course_codes)} course(s) to monitor")
    return semester, course_codes


def build_course_urls(semester, course_codes):
    """Build course URLs from semester and course codes."""
    urls = []
    for code in course_codes:
        url = f"{BASE_COURSE_URL}/{semester}/{code}/"
        urls.append(url)
    return urls


def play_alarm(course_name, status, page):
    """Play a loud alarm when a course opens up and open registration page."""
    log("🔔 PLAYING ALARM...")
    
    # Play system alert sound multiple times
    for _ in range(5):
        # Terminal bell
        print("\a", end="", flush=True)
        # macOS system sound (Sosumi is a loud alert sound)
        os.system('afplay /System/Library/Sounds/Sosumi.aiff 2>/dev/null &')
        time.sleep(0.3)
    
    # Speak alert message
    message = f"Alert! {course_name} is now {status}. Check registration immediately!"
    os.system(f'say "{message}" &')
    
    # Also try playing a few more system sounds
    os.system('afplay /System/Library/Sounds/Glass.aiff 2>/dev/null &')
    time.sleep(0.5)
    os.system('afplay /System/Library/Sounds/Basso.aiff 2>/dev/null &')
    
    # Open registration page in a new tab
    try:
        log(f"Opening registration page in a new tab: {REGISTRATION_URL}")
        with page.expect_popup() as popup_info:
            page.evaluate(f'window.open("{REGISTRATION_URL}", "_blank")')
        registration_page = popup_info.value
        log("✓ Registration page opened in new tab")
    except Exception as e:
        log(f"WARNING: Could not open registration page: {e}")


def get_status(page):
    """Extract the status text from the course page."""
    try:
        status_element = page.locator(STATUS_SELECTOR).first
        status_text = status_element.inner_text(timeout=5000).strip().lower()
        return status_text
    except PlaywrightTimeoutError:
        log("ERROR: Could not find status element on page")
        return None
    except Exception as e:
        log(f"ERROR: Failed to get status: {e}")
        return None


def wait_for_login(page, url):
    """Wait for user to complete login by detecting when page loads course details."""
    log(f"Navigating to {url}")
    page.goto(url, wait_until="networkidle")
    
    # Check if we're on the login page or the course page
    page_title = page.title()
    
    if "Sign in" in page_title or "Stale Request" in page_title:
        log("Waiting for you to login... (browser is open, please login manually)")
        log("The script will automatically detect when login is complete.")
        
        # Wait for the page title to change to the course page
        # Or wait for the status element to appear
        max_wait_time = 300  # 5 minutes max wait
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # Check if status element exists (means we're on course page)
                status_element = page.locator(STATUS_SELECTOR).first
                if status_element.is_visible(timeout=2000):
                    log("✓ Login detected! Course page loaded.")
                    return True
            except:
                pass
            
            # Also check title
            current_title = page.title()
            if LOGGED_IN_TITLE in current_title and "Sign in" not in current_title:
                log("✓ Login detected! Course page loaded.")
                return True
            
            time.sleep(2)  # Check every 2 seconds
        
        log("ERROR: Timeout waiting for login. Please try again.")
        return False
    else:
        # Already on course page (maybe already logged in)
        log("Already on course page (may already be logged in)")
        return True


def check_course_status(page, url, course_name):
    """Check the status of a single course."""
    try:
        log(f"Checking {course_name}...")
        page.reload(wait_until="networkidle", timeout=30000)
        
        status = get_status(page)
        if status:
            log(f"  Status: {status}")
            return status
        else:
            log(f"  ERROR: Could not determine status")
            return None
    except Exception as e:
        log(f"  ERROR: Failed to check course: {e}")
        return None


def monitor_courses():
    """Main monitoring function."""
    # Get course codes from user
    semester, course_codes = get_course_codes()
    if not semester or not course_codes:
        return
    
    # Build URLs from course codes
    course_urls = build_course_urls(semester, course_codes)
    course_names = [f"Course {code}" for code in course_codes]
    
    log("=" * 60)
    log("UT Registration Checker Starting")
    log(f"Monitoring {len(course_codes)} course(s): {', '.join(course_codes)}")
    log("=" * 60)
    
    with sync_playwright() as p:
        # Launch browser in headed mode so user can login
        # Try Firefox first (more stable on macOS), fallback to Chromium
        log("Launching browser...")
        browser = None
        try:
            # Try Firefox first - more stable on macOS
            log("Attempting to launch Firefox...")
            browser = p.firefox.launch(headless=False)
            log("✓ Firefox launched successfully")
        except Exception as e:
            log(f"Firefox launch failed: {e}")
            log("Trying Chromium with additional stability options...")
            try:
                # Try Chromium with additional launch args for stability
                browser = p.chromium.launch(
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                    ]
                )
                log("✓ Chromium launched successfully")
            except Exception as e2:
                log(f"ERROR: Both Firefox and Chromium failed to launch")
                log(f"Firefox error: {e}")
                log(f"Chromium error: {e2}")
                log("\nTrying to install Firefox browsers...")
                log("Run: python3.11 -m playwright install firefox")
                return
        
        context = browser.new_context()
        
        # Store pages for all courses
        pages = []
        
        try:
            # Step 1: Navigate to first course and wait for login
            log(f"\nOpening first course: {course_names[0]} ({course_codes[0]})")
            page1 = context.new_page()
            pages.append(page1)
            
            if not wait_for_login(page1, course_urls[0]):
                log("Failed to complete login. Exiting.")
                return
            
            # Step 2: Open remaining courses in new tabs (should already be logged in)
            if len(course_codes) > 1:
                log("\n" + "=" * 60)
                log("Opening additional course pages in new tabs...")
                for i in range(1, len(course_codes)):
                    log(f"Opening course {i+1}/{len(course_codes)}: {course_names[i]} ({course_codes[i]})")
                    try:
                        # Use JavaScript to open in a new tab, then wait for the popup
                        with page1.expect_popup() as popup_info:
                            page1.evaluate(f"window.open('{course_urls[i]}', '_blank')")
                        new_page = popup_info.value
                        pages.append(new_page)
                        
                        # Wait for the page to load
                        new_page.wait_for_load_state("networkidle", timeout=30000)
                        
                        # Verify page loaded correctly
                        status = get_status(new_page)
                        if status:
                            log(f"✓ Course {course_codes[i]} loaded. Status: {status}")
                        else:
                            log(f"WARNING: Could not verify course {course_codes[i]}. Continuing anyway...")
                    except Exception as e:
                        log(f"ERROR: Failed to open course {course_codes[i]}: {e}")
                        # Create page manually as fallback
                        new_page = context.new_page()
                        new_page.goto(course_urls[i], wait_until="networkidle", timeout=30000)
                        pages.append(new_page)
            
            # Step 3: Get initial statuses
            log("\n" + "=" * 60)
            log("Initial Status Check")
            log("=" * 60)
            initial_statuses = {}
            for i, (page, name) in enumerate(zip(pages, course_names)):
                status = check_course_status(page, course_urls[i], name)
                initial_statuses[name] = status
            
            # Step 4: Start monitoring loop
            log("\n" + "=" * 60)
            log(f"Starting monitoring loop (checking every {CHECK_INTERVAL_MINUTES} minutes)")
            log("Press Ctrl+C to stop")
            log("=" * 60 + "\n")
            
            check_count = 0
            while True:
                check_count += 1
                log(f"\n--- Check #{check_count} ---")
                
                for i, (page, name) in enumerate(zip(pages, course_names)):
                    status = check_course_status(page, course_urls[i], name)
                    
                    if status:
                        initial_status = initial_statuses.get(name, "unknown")
                        
                        # Check if status changed from "closed"
                        if initial_status == "closed" and status != "closed":
                            log("=" * 60)
                            log(f"🎉 ALERT: {name} STATUS CHANGED!")
                            log(f"   Previous: {initial_status}")
                            log(f"   Current:  {status}")
                            log(f"   URL: {course_urls[i]}")
                            log("=" * 60)
                            
                            # Update initial status so we don't alert again for same change
                            initial_statuses[name] = status
                            
                            # Play loud alarm and open registration page
                            play_alarm(name, status, page)
                
                log(f"\nNext check in {CHECK_INTERVAL_MINUTES} minutes...")
                time.sleep(CHECK_INTERVAL_SECONDS)
        
        except KeyboardInterrupt:
            log("\n\nMonitoring stopped by user.")
        except Exception as e:
            log(f"\n\nERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if browser:
                try:
                    log("\nClosing browser...")
                    browser.close()
                except Exception as e:
                    log(f"Error closing browser (may already be closed): {e}")
            log("Done.")


if __name__ == "__main__":
    monitor_courses()

