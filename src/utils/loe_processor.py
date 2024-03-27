import sys
sys.path.append('N:/Dev/AI/Underwriting/src/utils')
import os
import fitz
from langchain_openai  import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from load_config import LoadConfig, LoadPrompts

app_config = LoadConfig()
prompt_config = LoadPrompts()

class LOEProcessor:
    def __init__(self, client_dir):
        self.client_dir = client_dir

    def __load_loe(self):
        loe_file_path = ''
        for file_name in os.listdir(self.client_dir):
            if file_name.startswith(app_config.loe_identifier):
                loe_file_path = os.path.join(self.client_dir, file_name)
        if not loe_file_path:
            print("LOE file not found")

        document = fitz.open(loe_file_path)  # Open the PDF file
        text = ""
        for page in document:  # Iterate through each page
            text += page.get_text()  # Extract text from the page
        document.close()  # Close the document
        return text

    def extract_info(self):
        llm = ChatOpenAI(model_name=app_config.llm_engine, temperature=app_config.llm_temperature)
        messages = [
            SystemMessage(
                content=prompt_config.loe_system_prompt
            ),
            HumanMessage(
                content=self.__load_loe()
            )
        ]
        print(messages)
        response = llm.invoke(messages).content
        return response.split(" ; ")
