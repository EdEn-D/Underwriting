from typing import List

import fitz  # Import the PyMuPDF library
import os
from load_config import LoadConfig

app_config = LoadConfig()
class T4Processor:
    def __init__(self, client_dir):
        self.client_dir = client_dir
    def __load_t4(self) -> List:
        t4_file_path = []
        for file_name in os.listdir(self.client_dir):
            if file_name.startswith(app_config.t4_identifier):
                t4_file_path.append(os.path.join(self.client_dir, file_name))
        if not t4_file_path:
            print("T4 file not found")
            return []

    def __get_texts(self):
        pass
    def extract_info(self):
        pdf_paths = self.__load_t4()
        if not pdf_paths: return

        pdf_texts = []
        for path in pdf_paths:
            document = fitz.open(path)  # Open the PDF file
            text = ""
            for page in document:  # Iterate through each page
                text += page.get_text()  # Extract text from the page
            document.close()  # Close the document
            return text

        pdf_lines = ""#pdf_text.split('\n')
        i = pdf_lines.index('Employment income')
        t4_income = pdf_lines[i + 3]
        return t4_income
