import requests
import time
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError
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
    }

    try:
        page.goto(url, timeout=10000)
        page_loaded = True
        result["checks"]["page_loaded"] = True

    except PlaywrightTimeoutError:
        print("[FAIL] Page load timed out")

    except PlaywrightError as error:
        print(f"[FAIL] Playwright error: {error}")

    print("Website:", page.url)

    # Basic page checks
    print("[PASS] Page loaded")

    page_loaded = False

    try:
        page.goto(url, timeout=10000)
        page_loaded = True
        print("[PASS] Page loaded")

    except PlaywrightTimeoutError:
        print("[FAIL] Page load timed out")

    title_passed = check(
        page.title() == "Example title",
        "Title matches"
    )

    result["checks"]["title"] = title_passed

    content_passed = check(
        page.get_by_text("Example Domain").is_visible(),
        "Expected content visible"
    )   

    result["checks"]["content"] = content_passed

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