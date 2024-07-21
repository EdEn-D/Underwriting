import sys
# sys.path.append('N:/Dev/AI/Underwriting')
from .load_config import LoadConfig, LoadPrompts
from underwriting.tools import doc_tools
from langchain_openai  import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json, time
from ..tools.airtable_eval import log_eval_data

app_config = LoadConfig()
prompt_config = LoadPrompts()

DEBUG = False
LOGGING = True

class LOEProcessor:
    def __init__(self, input_file):
        self.input_file = input_file

    def extract_data(self):
        start_time = time.time()

        llm = ChatOpenAI(model_name=app_config.llm_lite_engine, temperature=app_config.llm_temperature)
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
        llm_response = llm.invoke(messages)
        response = llm_response.content

        # TODO: Is this the best way to do this? 
        # TODO: Move this to parsing_tools.py
        try:
            self.extracted_data = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}\n Response was not formatted as JSON. Returning raw response.")
            self.extracted_data = response
        except Exception as e:
            print(f"An error occurred when converting LOE response to JSON: {e}")
            self.extracted_data = response

        end_time = time.time()
        execution_time = end_time - start_time
        self.metadata = {
            'model': llm_response.response_metadata['model_name'],
            'execution_time': f"{execution_time:.2f}"
        }

        return_value = {"data" : self.extracted_data, "metadata" : self.metadata}

        if DEBUG:
            print("Returing LOE Data: ", return_value)

        if LOGGING:
            log_eval_data(return_value)
        return return_value
    
    def get_data(self):
        return self.extracted_data
