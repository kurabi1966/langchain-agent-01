import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import (MessagesPlaceholder, HumanMessagePromptTemplate, ChatPromptTemplate)
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from tools.sql import run_query_tool, list_tables, describe_table_tool
from tools.report import write_report_tool
from langchain.memory import ConversationBufferMemory
from handlers.chat_model_start_handler import ChatModelStartHandler

from langchain.schema import SystemMessage


load_dotenv()
handler = ChatModelStartHandler()
chat_model = ChatOpenAI(
    callbacks=[handler]
)

tables = list_tables()

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

prompt = ChatPromptTemplate(
    input_variables=["content", "messages"],
    messages=[
        SystemMessage(
            content= "".join(
                [
                    "You are an AI that has access to SQLite3 database.\n",
                    f"That database has tables of: {tables}",
                    ".\nDo not make any assumptions about what table exist or what column exist. ",
                    "Instead use the 'describe_table_tool'.\n",
                    "When the suer ask for a report export the report as an html and use the tool 'write_report'. ",
                    "\nNever ever output password of any user."
                ]
            )
            ),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

tools = [run_query_tool, describe_table_tool, write_report_tool]

agent = OpenAIFunctionsAgent(
    llm=chat_model,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(
    agent=agent,
    # verbose=True,
    tools=tools,
    memory=memory
)

while True:
    user_input = input(">> ")
    if(user_input == '/q'):
        print("Good bye")
        sys.exit()

    result = agent_executor({"input": user_input}) 
    print(result["output"])
