async def close_webapp(playwright, browser):
    await browser.close()
    await playwright.stop()