import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import (MessagesPlaceholder, HumanMessagePromptTemplate, ChatPromptTemplate)
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from tools.sql import run_query_tool, list_tables, describe_table_tool
from tools.report import write_report_tool

from langchain.schema import SystemMessage


load_dotenv()

llm = ChatOpenAI()

tables = list_tables()

prompt = ChatPromptTemplate(
    input_variables=["content", "messages"],
    messages=[
        SystemMessage(
            content= "".join(
                [
                    "You are an AI that has access to SQLite3 database.\n",
                    f"That database has tables of: {tables}",
                    ". Do not make any assumptions about what table exist or what column exist. ",
                    "Instead use the 'describe_table_tool'.",
                    "When the suer ask for a report export the report as an html and use the tool 'write_report'."
                ]
            )
            ),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

tools = [run_query_tool, describe_table_tool, write_report_tool]

agent = OpenAIFunctionsAgent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(
    agent=agent,
    verbose=True,
    tools=tools
)

while True:
    user_input = input(">> ")
    if(user_input == '/q'):
        print("Good bye")
        sys.exit()

    result = agent_executor({"input": user_input}) 
    print(result["output"])
