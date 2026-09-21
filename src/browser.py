import json
import logging
import time
from urllib.parse import urljoin

import requests
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

logging.basicConfig(
    filename="reports/automation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def check(condition, test_name):
    if condition:
        print(f"[PASS] {test_name}")
        return True

    print(f"[FAIL] {test_name}")
    return False


def check_link(url):
    try:
        response = requests.get(url, timeout=10)

        return response.status_code < 400, response.status_code

    except requests.RequestException as error:
        print(f"[ERROR] Could not check {url}: {error}")
        return False, None


logging.info("Starting website QA automation")

with sync_playwright() as p:
    start_time = time.time()
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    url = "https://example.com"

    result = {
        "website": url,
        "status": "FAIL",
        "duration": 0,
        "checks": {
            "page_loaded": False,
            "title": False,
            "content": False,
        },
        "links": {
            "checked": 0,
            "broken": 0,
        },
        "screenshot": "",
    }

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page_loaded = True
        result["checks"]["page_loaded"] = True
        logging.info(f"Page loaded successfully: {url}")
    except PlaywrightTimeoutError:
        page_loaded = False
        logging.error(f"Page load timeout: {url}")
    except PlaywrightError as error:
        page_loaded = False
        logging.error(f"Playwright error: {error}")

    print("Website:", page.url)

    title_passed = False
    content_passed = False

    if page_loaded:
        title_passed = check(
            page.title() == "Failed Domain",
            "Title matches"
        )
        result["checks"]["title"] = title_passed

        content_passed = check(
            page.get_by_text("Example Domain").is_visible(),
            "Expected content visible"
        )
        result["checks"]["content"] = content_passed

    else:
        logging.error("Page did not load successfully; skipping title/content checks.")

    # Link checks
    links = page.locator("a")
    link_count = links.count()

    print()
    print("Links found:", link_count)
    print()

    broken_links = 0
    links_checked = 0

    for i in range(link_count):
        href = links.nth(i).get_attribute("href")

        # Ignore links without href
        if not href:
            continue

        # Ignore non-web links
        if not href.startswith(("http://", "https://", "/")):
            continue

        # Convert relative URL into absolute URL
        full_url = urljoin(page.url, href)

        is_valid, status_code = check_link(full_url)

        if is_valid:
            print(f"[PASS] {full_url} ({status_code})")
        else:
            print(f"[FAIL] {full_url} ({status_code})")
            broken_links += 1
            links_checked += 1

    duration = round(time.time() - start_time, 2)

    result["duration"] = duration
    result["links"]["checked"] = links_checked
    result["links"]["broken"] = broken_links

    # Overall result
    print()
    print("Broken links:", broken_links)

    overall_passed = (
        page_loaded
        and title_passed
        and content_passed
        and broken_links == 0
    )

    result["status"] = "PASS" if overall_passed else "FAIL"
    print("Overall:", "PASS" if overall_passed else "FAIL")

    if not overall_passed:
        screenshot_path = "reports/screenshots/failure.png"
        page.screenshot(path=screenshot_path, full_page=True)
        result["screenshot"] = screenshot_path
        logging.error(f"Test failed. Screenshot saved: {screenshot_path}")

    logging.info(f"Automation completed with status: {result['status']}")

    print()
    print("Test Result")
    print("-----------")
    print("Website:", result["website"])
    print("Status:", result["status"])
    print("Duration:", result["duration"], "seconds")
    print()
    print("Checks:")
    print("  Page loaded:", result["checks"]["page_loaded"])
    print("  Title:", result["checks"]["title"])
    print("  Content:", result["checks"]["content"])
    print()
    print("Links:")
    print("  Checked:", result["links"]["checked"])
    print("  Broken:", result["links"]["broken"])

    browser.close()

    with open("reports/report.json", "w") as file:
        json.dump(result, file, indent=4)

    print("Report saved: reports/report.json")