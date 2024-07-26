# external package imports
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.globals import set_debug, set_verbose
from playwright.async_api import async_playwright

import asyncio
import langchain
import os

# local imports
from model import Agent
from webpage import close_webapp

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find and remove the <head> section
    if soup.head:
        soup.head.decompose()
    for script in soup.find_all('script'):
        script.decompose()
    html_content = str(soup)

    return html_content

def verify_success(html):
    return ("welcome" in html.lower()) or ("success" in html.lower())

async def main():
    # load the environment variables
    load_dotenv()

    # sets debug modes
    # set_debug(True)
    # set_verbose(True)
    # langchain.debug = True

    # start the sql injector / hacker
    agent = Agent(os.environ["VECTORSTORE_PATH"])

    # start instance of the web app using playwright
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("http://localhost:3000")
        await page.wait_for_load_state('domcontentloaded')
        # html_content = await page.content()

        # # parse the html content - removes head and script tags
        # html_content = parse_html(html_content)

        # print("html content: ", html_content)

        usernames = []
        passwords = []

        attempts = 5
        success = False
        previous = ""
        while (not success and attempts > 0):
            html_content = await page.content()
            await page.wait_for_load_state('domcontentloaded')
            html_content = parse_html(html_content)
            if (verify_success(html_content)):
                print("Successfully logged in")
                break

            plan, code, username, password = await agent.run(html_content, None if previous == "" else previous)
            print("Plan: ", plan)
            usernames.append(username)
            passwords.append(password)
            previous += f"\nPayload {6-attempts}:\nUsername: {username}, Password: {password}\n"
            print("CODE:\n", code)
            # execute the code
            try:
                compiled_code = compile(code, '<string>', 'exec')
                global_namespace = {'page': page,
                                     'browser': browser,
                                     'playwright': playwright}
                local_namespace = {}

                exec(compiled_code, global_namespace, local_namespace)
                f = local_namespace['func']

                await f()
                await page.wait_for_load_state('domcontentloaded')
                print("Payload injected and site loaded")

                # extract the new html and check if the code successfully logged in
                new_html_content = await page.content()

                new_soup = parse_html(new_html_content)

                # CURRENT verification method, will be more sophisticated in the future
                if ("welcome" in new_soup.lower()) or ("success" in new_soup.lower()):
                    success = True
                    print("Successfully logged in")
                else:
                    print("Failed to log in")

                # update the html to the new content
                html_content = new_soup

            except Exception as e:
                print("Error: ", e)


            attempts -= 1

        if not success:
            print("Failed to log in after 5 attempts")

        print("Attempted usernames: ", usernames)
        print("Attempted passwords: ", passwords)

        # end the program
        await close_webapp(playwright, browser)

if __name__ == '__main__':
    asyncio.run(main())