from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://pancharasshubham.com")

    print("URL:", page.url)
    print("Title:", page.title())

    browser.close()