from playwright.sync_api import sync_playwright

# TODO - visits the website, and attempts to find username and password and click it
def create_page(site: str):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False, slow_mo=5000)
    page = browser.new_page()
    page.goto(site)
    return playwright, browser, page
    # with sync_playwright() as p:
    #     # launches the browser
    #     browser = p.chromium.launch(headless=False, slow_mo=1000)
    #     # create a new page
    #     page = browser.new_page()
    #     # navigate to the page
    #     page.goto("localhost:3000")
    #     # locate a link element with "Docs" text
    #     docs_button = page.get_by_role("button", name="Docs")
    #     docs_button.click()
    #     # close the browser
    #     browser.close()
def close_webapp(playwright, browser):
    browser.close()
    playwright.stop()
