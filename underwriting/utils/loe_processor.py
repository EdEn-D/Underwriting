import sys
# sys.path.append('N:/Dev/AI/Underwriting')
from .load_config import LoadConfig, LoadPrompts
from underwriting.tools import doc_tools
from langchain_openai  import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json

app_config = LoadConfig()
prompt_config = LoadPrompts()

DEBUG = False

class LOEProcessor:
    def __init__(self, input_file):
        self.input_file = input_file


    def extract_data(self):
        llm = ChatOpenAI(model_name=app_config.llm_engine, temperature=app_config.llm_temperature)
        messages = [
            SystemMessage(
                content=prompt_config.loe_system_prompt
            ),
            HumanMessage(
                content=doc_tools.extract_text_from_pdf(self.input_file)
            )
        ]
        if DEBUG:
            print(messages)
        response = llm.invoke(messages).content
        # self.extracted_data = json.loads(response)

        try:
            self.extracted_data = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}\n Response was not formatted as JSON. Returning raw response.")
            self.extracted_data = response
        except Exception as e:
            print(f"An error occurred when converting LOE response to JSON: {e}")
            self.extracted_data = response

        return self.extracted_data
    
    def get_data(self):
        return self.extracted_data
