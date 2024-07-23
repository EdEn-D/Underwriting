from typing import List

import fitz  # Import the PyMuPDF library
import os
from .load_config import LoadConfig

import pytesseract
from pytesseract import Output
from pdf2image import convert_from_path
import re

app_config = LoadConfig()

# T4 Processor currently assumes the T4 the official computer generated T4 document (other documents cannot be officially used anyways)
# Doesn't work, should implement a CSV solution
# TODO: Find a way to check that the official document is provided
class T4Processor:
    def __init__(self, client_dir):
        self.client_dir = client_dir
        # self.test_file = 'N:/Dev/AI/Underwriting/data/clients/Hemat and Amy/Hemant/Hemant Sud 2021 T4.pdf'

    def __load_t4(self) -> List:
        t4_file_path = []
        for file_name in os.listdir(self.client_dir):
            if file_name.startswith(app_config.t4_identifier):
                t4_file_path.append(os.path.join(self.client_dir, file_name))
        if not t4_file_path:
            raise FileNotFoundError("T4 file not found")

        return t4_file_path
    

    def __get_texts(self):
        pdf_paths = self.__load_t4()
        if not pdf_paths:
            raise RuntimeError("Error while loading the T4 document")

        pdf_texts = []
        for path in pdf_paths:
            document = fitz.open(path)
            text = ""
            for page in document:
                text += page.get_text()
            document.close()
            pdf_texts.append(text)

        return pdf_texts
    
    
    def extract_info(self):

        texts = self.__get_texts()

        t4_income = []
        for text in texts:
            pdf_lines = text.split('\n')
            print(pdf_lines)
            i = pdf_lines.index('Employment income')
            t4_income.append(pdf_lines[i + 3])

        return t4_income

#     def extract_from_img(self):
#         images = convert_from_path(self.test_file)
#         text = pytesseract.image_to_string(images[0], lang='eng', output_type=Output.STRING)
#         print("PDF text detected: \n" + text)
#         box_14_pattern = r"(Box 14|Employment Income)[^\d]*(\d+\.\d{2})"
#         match = re.search(box_14_pattern, text)
#         if match:
#             box_14_value = match.group(2)  # The second group should be the numeric value
#             print(f"Box 14 (Employment Income) Value: {box_14_value}")
#         else:
#             print("Box 14 information not found.")
#
# pytesseract.pytesseract.tesseract_cmd = r'N:\Program Files\Tesseract-OCR\tesseract.exe'
# t4 = T4Processor("nothing").extract_from_img()