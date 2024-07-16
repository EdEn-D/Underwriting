import sys
# sys.path.append('N:/Dev/AI/Underwriting')
from .load_config import LoadConfig, LoadPrompts
from underwriting.tools import doc_tools
from langchain_openai  import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

app_config = LoadConfig()
prompt_config = LoadPrompts()

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
        print(messages)
        response = llm.invoke(messages).content
        self.extracted_data = response.split(" ; ")
        return self.extracted_data
    
    def get_data(self):
        return self.extracted_data
