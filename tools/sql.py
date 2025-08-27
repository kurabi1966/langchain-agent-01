import sqlite3

from langchain.tools import Tool

from pydantic.v1 import BaseModel
from typing import List

conn = sqlite3.connect("db.sqlite")

class RunQueryArgsSchema(BaseModel):
    query: str

def describe_table(table_name: str):
    c = conn.cursor()
    c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name = ?", (table_name,))
    rows = c.fetchall()
    return "\n".join(row[0] for row in rows if row[0] is not None)

def list_tables():
    c = conn.cursor()
    c.execute("SELECT NAME FROM sqlite_master WHERE type='table';")
    rows = c.fetchall()
    return "\n".join(row[0] for row in rows if row[0] is not None)

def run_sqlite_query(query):
    c = conn.cursor()
    try:
        c.execute(query)
        return c.fetchall()
    except sqlite3.OperationalError as err:
        return f"The following error occurred: {str(err)} "

run_query_tool = Tool.from_function(
    name="run_sqlite_query",
    description="Run a sqlite query.",
    func=run_sqlite_query,
    args_schema=RunQueryArgsSchema
)
 

describe_table_tool = Tool.from_function(
    name="describe_table",
    description="Given a single table name, return the schema of this table.",
    func=describe_table
)