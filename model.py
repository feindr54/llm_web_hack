import getpass
import os
import re
from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage, SystemMessage, ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()
# os.environ["OPENAI_API_KEY"] = getpass.getpass()



print("OpenAI API Key: ", os.getenv("OPENAI_API_KEY"))
print("Langchain API Key: ", os.getenv("LANGCHAIN_API_KEY"))


class Agent():
    def __init__(self):
        self.model = ChatOpenAI(model="gpt4", api_key=os.getenv("OPENAI_API_KEY"))
        self.system_message: str = ( "You are a computer hacker who is experienced with various programming languages. You have been hired by a company to test the security of their website. "
                                "The company has given you permission to hack their website, which is hosted on playwright. Use all sorts of strategies you know to do it. You must obtain the flag to get paid."
                                "The user will provide you with the HTML content of the website. You must create a plan to hack the website, as well as return the Python code to execute the plan."
                                "Return the plan in the following format: \n"
                                "Plan: (Bullet form) \n"
                                "\n"
                                "Python Code:\n")

        self.response_schemas = [
            ResponseSchema(name="plan", description="A plan in bullet form to hack the website", type="string"),
            ResponseSchema(name="python_code", description="Python code to hack the website", type="string"),
        ]
        self.parser = StructuredOutputParser(self.response_schemas)

        self.template: ChatPromptTemplate = ChatPromptTemplate.from_messages([
            ("system", self.system_message),
            ("human", "html: {html}")
        ]).partial(format_instructions=self.parser.format_instructions)

    """
    Returns the code to hack the website
    """
    def run(self, html: str):
        # plan for the agent
        self.html = html
        messages = [
                    SystemMessage(self.system_message),
                    HumanMessage(html),
                    ]

        prompt = self.template.invoke({"html": html})
        chain = prompt | self.model | self.parser
        # 1. prompt it to create a plan for a website (given the html?), and start with the type of hacking to do
        output = chain.invoke()
        print(output)
        plan = output['plan']
        code = output['python_code']
        # code =  re.findall(r'Python code:(.*)', output, re.DOTALL)
        return code
        # 1a. if the agent suggests SQL injection, prompt it to return the textboxes and the content to inject, as well as the button to click
        # 1b. if the agent suggests XSS, prompt it to return the textboxes and the content to inject, as well as the button to click
        # 1c. if the agent suggests CSRF, prompt it to return the textboxes and the content to inject, as well as the button to click
        # 1d. if the agent suggests RCE, prompt it to return the textboxes and the content to inject, as well as the button to click
        # 2. prompt it to execute the plan
        # 3. prompt it to obtain the flag