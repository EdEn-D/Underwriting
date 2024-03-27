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

from nanonets import NANONETSOCR
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
        # self.payslip_paths = self.__load_payslip()
        self.__define_output_directories()
        self.nanonets_table_extract()

        self.table_paths = self.extract_tables_to_csv(self.nano_extracted_tables_csv_path, self.extracted_csvs_path)
        self.table_dfs = self.extract_tables_to_dfs(self.nano_extracted_tables_csv_path)
        self.table_text = self.extract_text_from_pdf(self.input_file) # TODO: Generalize this to more than 1 document
        self.__define_agents()

    def __define_output_directories(self):
        # Extracted tables:
        self.extracted_csvs_path = os.path.join(os.path.dirname(self.input_file),
                                           os.path.splitext(os.path.basename(self.input_file))[0] + " extracted_tables")
        os.makedirs(self.extracted_csvs_path, exist_ok=True)
        self.nano_extracted_tables_csv_path = os.path.join(str(self.extracted_csvs_path), os.path.splitext(os.path.basename(self.input_file))[0] + "_extracted_tables.csv")

    # def __load_payslip(self):
    #     payslip_file_paths = []
    #     for file_name in os.listdir(self.client_dir):
    #         full_path = os.path.join(self.client_dir, file_name)
    #         if os.path.isfile(full_path) and file_name.startswith(app_config.payslip_identifier):
    #             payslip_file_paths.append(os.path.join(self.client_dir, file_name))
    #     if not payslip_file_paths:
    #         raise FileNotFoundError("payslip file not found")
    #
    #     print("Payslips Loaded: ")
    #     print(payslip_file_paths)
    #     return payslip_file_paths

    def nanonets_table_extract(self):
        if os.path.exists(self.nano_extracted_tables_csv_path):
            print("Tables already extracted with Nanonets")
            return

        model = NANONETSOCR()
        model.set_token(os.getenv("NANONESTS_TABLE_MODEL_TOKEN"))
        model.convert_to_csv(self.input_file, output_file_name=self.nano_extracted_tables_csv_path)

    def extract_tables_to_csv(self, csv_file_path, output_path):
        def save_table(table_lines, table_number, output_folder):
            output_file_path = os.path.join(output_folder, f"Table_{table_number}.csv")

            # Check if the first row is empty or contains only commas
            if not any(table_lines[0]) or all(cell == '' for cell in table_lines[0]):
                table_lines = table_lines[1:]  # Remove the first row if it's empty

            with open(output_file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(table_lines)
            print(f"Table {table_number} saved to {output_file_path}")
            return output_file_path  # Return the path to the saved file

        # Create output folder path
        output_folder = output_path  # os.path.join(csv_directory, csv_name_without_ext)

        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Initialize variables
        current_table_number = 0
        current_table_lines = []
        table_started = False
        table_paths = []  # Initialize an empty list to store file paths

        # Read the CSV file
        with open(csv_file_path, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                # Convert row list to string to check if it's a table header
                row_str = ','.join(row)
                if row_str.startswith('TABLE '):
                    # If we're already in a table, save the current table
                    if table_started:
                        path = save_table(current_table_lines, current_table_number, output_folder)
                        table_paths.append(path)  # Add the path to the list
                        current_table_lines = []  # Reset for the next table
                    current_table_number += 1
                    table_started = True  # Start a new table
                elif table_started:
                    # Add row to current table
                    current_table_lines.append(row)

        # Save the last table after file ends
        if table_started:
            save_table(current_table_lines, current_table_number, output_folder)
            table_paths.append(path)  # Add the path to the list

        return table_paths

    def extract_tables_to_dfs(self, csv_file_path):
        # Initialize variables
        current_table_number = 0
        current_table_lines = []
        table_started = False
        dfs = []  # Initialize an empty list to store DataFrames

        # Read the CSV file
        with open(csv_file_path, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                # Check if it's a table header
                row_str = ','.join(row)
                if row_str.startswith('TABLE '):
                    # If we're already in a table, convert the current table to a DataFrame
                    if table_started:
                        df = pd.DataFrame(current_table_lines[1:], columns=current_table_lines[0])
                        dfs.append(df)
                        current_table_lines = []  # Reset for the next table
                    current_table_number += 1
                    table_started = True  # Start a new table
                elif table_started:
                    # Add row to current table
                    current_table_lines.append(row)

        # Convert the last table to a DataFrame after file ends, if any
        if table_started:
            df = pd.DataFrame(current_table_lines[1:], columns=current_table_lines[0])
            dfs.append(df)

        return dfs

    def extract_text_from_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        text = ''
        for page in doc:
            text += page.get_text()
        doc.close()

        return text

    def process_payslips(self):
        self.table_paths = self.extract_tables_to_csv(self.nano_extracted_tables_csv_path, self.extracted_csvs_path)
        self.table_dfs = self.extract_tables_to_dfs(self.nano_extracted_tables_csv_path)
        self.table_text = self.extract_text_from_pdf(self.client_dir)

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


    def __extract_numerical_value(self, text):
        # Regular expression to match a sequence of digits that may contain a decimal point
        match = re.search(r'\d+\.\d+|\d+', text)
        if match:
            return float(match.group())
        else:
            return None
    def get_earnings(self, earning_type, agent='csv'):
        # if agent == 'csv':
        engine = self.csv_chat_agent
        if agent == 'df':
            engine = self.dfs_chat_agent

        if earning_type == "regular":
            prompt = prompt_config.payslip_regular_earnings
        elif earning_type == "ytd":
            prompt = prompt_config.payslip_ytd_earnings

        output = engine.invoke(prompt)["output"]
        return self.__extract_numerical_value(output)
