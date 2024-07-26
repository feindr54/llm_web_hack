from webpage import close_webapp, create_page
from model import Agent
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

import langchain
import os
from langchain.globals import set_debug, set_verbose

import asyncio
from dotenv import load_dotenv



async def main():
    async def test():
        import asyncio

        # List of common username and password combinations
        credentials = [
            ('admin', 'admin'),
            ('user', 'password'),
            ('root', 'toor'),
            ('guest', 'guest')
        ]

        for username, password in credentials:
            # Input username
            await page.fill('#username', username)
            # Input password
            await page.fill('#password', password)
            # Click the 'Enter' button
            await page.click('button[type="button"]')

            # Wait for navigation or some indication of login success
            await page.wait_for_timeout(2000)  # Wait for 2 seconds to see if login is successful
    load_dotenv()
    set_debug(True)
    set_verbose(True)
    langchain.debug = True
    # TODO - start the sql injector / hacker
    agent = Agent(os.environ["VECTORSTORE_PATH"])

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

        attempts = 1
        success = False
        previous = ""
        while (not success and attempts > 0):
            plan, code = await agent.run(html_content, None if previous == "" else previous)
            previous += f"\nPlan {2-attempts}:\n" + plan + '\n'
            print("code: ", code)
            # execute the code
            try:
                compiled_code = compile(code, '<string>', 'exec')
                global_namespace = {'page': page,
                                     'browser': browser,
                                     'playwright': playwright}
                local_namespace = {}

                exec(compiled_code, global_namespace, local_namespace)
                # import types
                # func = types.FunctionType(globals()['func'])
                # await self.func()
                f = local_namespace['func']

                print("Saved func")
                await asyncio.wait_for(f(), timeout=15.0)
                print("Executed func")

                # TODO: extract the new html and check if the code successfully logged in
                new_html_content = await page.content()

                new_soup = BeautifulSoup(new_html_content, 'html.parser')
                print(new_soup.get_text())
                if "logged in" or "success" in new_soup.get_text().lower():
                    success = True
                    print("Successfully logged in")
                else:
                    print("Failed to log in")

            except Exception as e:
                print("Error: ", e)


            attempts -= 1

        if not success:
            print("Failed to log in after 5 attempts")
        # exec(code)

    # TODO - somehow parse the code and see if it is valid python code
    # TODO - execute the code on the webapp

    # end the program
        await close_webapp(playwright, browser)

if __name__ == '__main__':
    asyncio.run(main())