from playwright.sync_api import sync_playwright

def check(condition, test_name):
    if condition:
        print(f"[PASS] {test_name}")
        return True

    print(f"[FAIL] {test_name}")
    return False

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://example.com")

    print("Website:", page.url)
    print("[PASS] Page loaded")
    print()

    title_passed = check(
        page.title() == "Example Domain",
        "Title matches"
    )

    content_passed = check(
        page.get_by_text("Example Domain").is_visible(),
        "Expected content visible"
    )

    overall_passed = title_passed and content_passed

    print()
    print("Overall:", "PASS" if overall_passed else "FAIL")

    browser.close()