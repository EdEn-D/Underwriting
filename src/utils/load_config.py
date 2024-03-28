import os
from dotenv import load_dotenv, find_dotenv
import yaml
from langchain_openai import OpenAIEmbeddings
from pyprojroot import here

load_dotenv(find_dotenv())


class LoadConfig:
    def __init__(self) -> None:
        with open(here("configs/app_config.yml")) as cfg:
            app_config = yaml.load(cfg, Loader=yaml.FullLoader)

        # LLM configs
        self.llm_engine = app_config["llm_config"]["engine"]
        self.llm_temperature = app_config["loe_llm_config"]["temperature"]
        # self.loe_llm_system_role = app_config["loe_llm_config"]["loe_llm_system_role"]
        self.persist_directory = str(here(
            app_config["directories"]["persist_directory"]))  # needs to be string for summation in chromadb backend: self._settings.require("persist_directory") + "/chroma.sqlite3"
        self.embedding_model = OpenAIEmbeddings()

        # Retrieval configs
        self.client_data_directory = app_config["directories"]["client_data_directory"]
        self.k = app_config["retrieval_config"]["k"]
        self.chunk_size = app_config["splitter_config"]["chunk_size"]
        self.chunk_overlap = app_config["splitter_config"]["chunk_overlap"]

        # Load OpenAI credentials
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        # File identifiers
        self.loe_identifier = app_config["file_identifiers"][("loe_identifier")]
        self.t4_identifier = app_config["file_identifiers"][("t4_identifier")]
        self.payslip_identifier = app_config["file_identifiers"][("payslip_identifier")]
        # clean up the upload doc vectordb if it exists
        self.create_directory(self.persist_directory)

    def create_directory(self, directory_path: str):
        """
        Create a directory if it does not exist.

        Parameters:
            directory_path (str): The path of the directory to be created.
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)


class LoadPrompts:
    def __init__(self) -> None:
        with open(here("configs/prompt_config.yml")) as cfg:
            prompt_config = yaml.load(cfg, Loader=yaml.FullLoader)

        self.loe_system_prompt = prompt_config["loe_prompts"]["llm_system_role"]
        self.payslip_regular_earnings = prompt_config["payslip_prompts"]["regular_earnings_prompt"]
        self.payslip_ytd_earnings = prompt_config["payslip_prompts"]["ytd_earnings_prompt"]
        self.payslip_dates = prompt_config["payslip_prompts"]["payment_date_prompt"]