from langchain.prompts.chat import ChatPromptTemplate
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import os

# for future RAG use
# from langchain_chroma import Chroma
# from langchain_core.runnables import RunnablePassthrough

# Pydantic output parsers
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
        self.method_parser = PydanticOutputParser(pydantic_object=Method)
        self.plan_parser = PydanticOutputParser(pydantic_object=Plan)

        self.method_template: ChatPromptTemplate = ChatPromptTemplate.from_messages([
            ("system", os.getenv('SYSMSG1')),
            ("human", "The html is: {html}\n{format_instructions}")
        ]).partial(format_instructions=self.method_parser.get_format_instructions())

        self.code_template: ChatPromptTemplate = ChatPromptTemplate.from_messages([
            ("system", os.getenv("SYSMSG2")),
            ("human", "\n{format_instructions}")
        ]).partial(format_instructions=self.plan_parser.get_format_instructions())

        # future uses in RAG
        # self.vectorstore = Chroma(persist_directory=vectorstore_path, embedding_function=OpenAIEmbeddings())
        # self.retriever = self.vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 1})

    # def format_docs(self, docs):
    #     return "\n\n".join(doc.page_content for doc in docs)

    """
    Returns the code to hack the website
    """
    async def run(self, html: str, previous):
        # plan for the agent
        self.html = html
        previous = "No previous plans" if previous is None else previous

        plan_chain = self.method_template | self.model | self.method_parser
        output = plan_chain.invoke({"html": html, "previous": previous})
        plan = output.plan

        code_chain = self.code_template | self.model | self.plan_parser
        output = code_chain.invoke({"plan": plan, "html": html})

        return plan, output.python_code, output.username, output.password