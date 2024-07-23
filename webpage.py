from playwright.async_api import async_playwright

# TODO - visits the website, and attempts to find username and password and click it
async def create_page(site: str):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False, slow_mo=10000)
    page = await browser.new_page()
    await page.goto(site)
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
async def close_webapp(playwright, browser):
    await browser.close()
    await playwright.stop()
