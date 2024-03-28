import os
from dotenv import load_dotenv, find_dotenv
from pprint import pprint, pformat
import fitz  # Import the PyMuPDF library
import csv
import pandas as pd

from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent, create_pandas_dataframe_agent
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from langchain_openai import ChatOpenAI, OpenAI
from langchain.prompts import PromptTemplate
from langsmith import Client

from src.tools import doc_tools, parsing_tools


from load_config import LoadConfig, LoadPrompts
from typing import List
import re

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = f"Underwriting project"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
client = Client()

load_dotenv(find_dotenv())
app_config = LoadConfig()
prompt_config = LoadPrompts()


# Todo try to output JSON straight from the llm, same for LOE processor
class PayslipProcessor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.__define_output_directories()
        self.__process_payslips()
        self.__define_agents()

    def __define_output_directories(self):
        # Extracted tables:
        self.extracted_csvs_path = os.path.join(os.path.dirname(self.input_file),
                                           os.path.splitext(os.path.basename(self.input_file))[0] + " extracted_tables")
        os.makedirs(self.extracted_csvs_path, exist_ok=True)
        self.nano_extracted_tables_csv_path = os.path.join(str(self.extracted_csvs_path), os.path.splitext(os.path.basename(self.input_file))[0] + "_extracted_tables.csv")

    def __process_payslips(self):
        doc_tools.nanonets_table_extract(self.nano_extracted_tables_csv_path, self.input_file)
        self.table_paths = doc_tools.extract_tables_to_csv(self.nano_extracted_tables_csv_path, self.extracted_csvs_path)
        self.table_dfs = doc_tools.extract_tables_to_dfs(self.nano_extracted_tables_csv_path)
        self.table_text = doc_tools.extract_text_from_pdf(self.input_file)

    def __define_agents(self):
        self.dfs_chat_agent = create_pandas_dataframe_agent(
            ChatOpenAI(temperature=0, model=app_config.llm_engine),
            self.table_dfs,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
        )

        self.csv_chat_agent = create_csv_agent(
            ChatOpenAI(temperature=0, model=app_config.llm_engine),
            self.table_paths,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
        )
        self.text_chat = ChatOpenAI(temperature=0, model=app_config.llm_engine)


    def get_earnings(self, earning_type, agent='csv'):
        if agent == 'csv':
            engine = self.csv_chat_agent
        elif agent == 'df':
            engine = self.dfs_chat_agent
        else:
            raise ValueError(f"Unsupported agent type: {agent}")

        if earning_type == "regular":
            print("Getting regular earnings...")
            prompt = prompt_config.payslip_regular_earnings
        elif earning_type == "ytd":
            print("Getting YTD earnings...")
            prompt = prompt_config.payslip_ytd_earnings
        else:
            raise ValueError(f"Unsupported earning type: {earning_type}")

        output = engine.invoke(prompt)["output"]
        return str(parsing_tools.extract_numerical_value(output))

    def get_payslip_dates(self):
        prompt = PromptTemplate.from_template(prompt_config.payslip_dates)
        prompt = prompt.format(text=self.table_text)
        return str(self.text_chat.invoke(prompt).content)