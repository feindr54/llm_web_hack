from webpage import close_webapp, create_page
from model import Agent
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

import asyncio
from dotenv import load_dotenv

async def main():
    load_dotenv()
    # TODO - start the sql injector / hacker
    agent = Agent()

    # start instance of the web app using playwright
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("http://localhost:3000")
        await page.wait_for_load_state('domcontentloaded')
        html_content = await page.content()

        # TODO - remove the head in the html code
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find and remove the <head> section
        if soup.head:
            soup.head.decompose()
        for script in soup.find_all('script'):
            script.decompose()
        html_content = str(soup)

        print("html content: ", html_content)

        code = agent.run(html_content)

        print("code: ", code)

        exec(code)

    # TODO - somehow parse the code and see if it is valid python code
    # TODO - execute the code on the webapp

    # end the program
        await close_webapp(playwright, browser)

if __name__ == '__main__':
    asyncio.run(main())