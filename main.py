from webpage import close_webapp, create_page
from model import Agent


if __name__ == '__main__':
    # TODO - start the sql injector / hacker
    agent = Agent()

    # start instance of the web app using playwright
    playwright, browser, page = create_page("http://localhost:3000")
    html_content = page.content()

    code = agent.run(html_content)

    # TODO - somehow parse the code and see if it is valid python code
    # TODO - execute the code on the webapp

    # end the program
    close_webapp(playwright, browser)