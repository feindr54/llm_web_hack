import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel, Field
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough

class Method(BaseModel):
    method: str = Field(description="The method to hack the website", type="string")
    plan: str = Field(description="How you plan to execute the method", type="string")

class Plan(BaseModel):
    python_code: str = Field(description="Python code to bypass the login")
    username: str = Field(description="if the plan required exploiting certain login credentials, the username used to login")
    password: str = Field(description="if the plan required exploiting certain login credentials, the password used to login")


os.environ["LANGCHAIN_TRACING_V2"] = "true"

class Agent():
    def __init__(self, vectorstore_path):
        self.model = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
        system_message: str = os.getenv("SYSMSG1")
        print(system_message)

        # self.response_schemas = [
        #     ResponseSchema(name="plan", description="A conceptual plan to hack the website, and overall strategy type", type="string"),
        #     ResponseSchema(name="python_code", description="Python code to hack the website", type="string"),
        # ]
        # self.parser = StructuredOutputParser.from_response_schemas(self.response_schemas)
        self.method_parser = PydanticOutputParser(pydantic_object=Method)
        self.plan_parser = PydanticOutputParser(pydantic_object=Plan)

        self.method_template: ChatPromptTemplate = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "The html is: {html}\n{format_instructions}")
        ]).partial(format_instructions=self.method_parser.get_format_instructions())

        self.code_template: ChatPromptTemplate = ChatPromptTemplate.from_messages([
            ("system", os.getenv("SYSMSG2")),
            ("human", "\n{format_instructions}")
        ]).partial(format_instructions=self.plan_parser.get_format_instructions())

        self.vectorstore = Chroma(persist_directory=vectorstore_path, embedding_function=OpenAIEmbeddings())
        self.retriever = self.vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 1})

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    """
    Returns the code to hack the website
    """
    async def run(self, html: str, previous):
        # plan for the agent
        self.html = html
        previous = "No previous plans" if previous is None else previous

        method_prompt = self.method_template
        print("prompt: ", method_prompt)

        # code = "print('Hello, World!')"
        chain1 = method_prompt | self.model | self.method_parser
        output = chain1.invoke({"html": html, "previous": previous})
        print(output)

        plan = output.plan


        # docs = self.retriever.invoke(dummy_method)
        # context = self.format_docs(docs)
        # print("context: ", context)
        plan_chain = self.code_template | self.model | self.plan_parser
        output = plan_chain.invoke({"plan": plan, "html": html})

        print(output)
        # chain ={"context": self.retriever | self.format_docs, "html": RunnablePassthrough()} | prompt | self.model
        # # # 1. prompt it to create a plan for a website (given the html?), and start with the type of hacking to do
        # output = chain.invoke({"html": html})
        # print(output)
        # plan = output.plan
        # code = output.python_code

        # print("plan: ", plan)

        return plan, output.python_code
        # 1a. if the agent suggests SQL injection, prompt it to return the textboxes and the content to inject, as well as the button to click
        # 1b. if the agent suggests XSS, prompt it to return the textboxes and the content to inject, as well as the button to click
        # 1c. if the agent suggests CSRF, prompt it to return the textboxes and the content to inject, as well as the button to click
        # 1d. if the agent suggests RCE, prompt it to return the textboxes and the content to inject, as well as the button to click
        # 2. prompt it to execute the plan
        # 3. prompt it to obtain the flag