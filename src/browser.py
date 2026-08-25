import requests
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
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    try:
        page.goto("https://example.com", timeout=10000)
        page_loaded = True
        print("[PASS] Page loaded")

    except PlaywrightTimeoutError:
        print("[FAIL] Page load timed out")

    except PlaywrightError as error:
        print(f"[FAIL] Playwright error: {error}")

    print("Website:", page.url)

    # Basic page checks
    print("[PASS] Page loaded")

    page_loaded = False

    try:
        page.goto("https://example.com", timeout=10000)
        page_loaded = True
        print("[PASS] Page loaded")

    except PlaywrightTimeoutError:
        print("[FAIL] Page load timed out")

    title_passed = check(
        page.title() == "Example Domain",
        "Title matches"
    )

    content_passed = check(
        page.get_by_text("Example Domain").is_visible(),
        "Expected content visible"
    )

    # Link checks
    links = page.locator("a")
    link_count = links.count()

    print()
    print("Links found:", link_count)
    print()

    broken_links = 0

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

    # Overall result
    print()
    print("Broken links:", broken_links)

    overall_passed = (
        page_loaded
        and title_passed
        and content_passed
        and broken_links == 0
    )

    print()
    print("Overall:", "PASS" if overall_passed else "FAIL")

    browser.close()