from typing import List

import fitz, os, csv
import pandas as pd
from nanonets import NANONETSOCR
from paddleocr import PaddleOCR,draw_ocr
from pdf2image import convert_from_path
from PIL import Image
import numpy as np

DEBUG = False

def extract_text_from_pdf(pdf_path, output_path='', source='txt') -> str:
    file_name = os.path.basename(pdf_path).split('.')[0] # Get the file name without the extension
    if not output_path:
        output_path = os.path.dirname(pdf_path)
    output_file_path = os.path.join(output_path, f"{file_name} extracted {source}.txt") 
    # Check if the extracted text file already exists to avoid re-extraction
    if os.path.exists(output_file_path):
        if DEBUG:
            print(f"Extracted {source} file found. Reading from it...")
        with open(output_file_path, 'r') as file:
            if DEBUG:
                print(file.read())

    # Extract text from the PDF
    text = ''
    if source == 'txt':
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    elif source == 'ocr':
        if not ocr:
            ocr = PaddleOCR(use_angle_cls=False, lang='en', use_gpu=True) # need to run only once to download and load model into memory
        images = convert_from_path(pdf_path)
        for pil_image in images:
            image = np.array(pil_image)
            ocr_result = ocr.ocr(image, cls=True)
            for line in ocr_result:
                line_text = "\n".join([text_info[-1][0] for text_info in line])
                text += line_text

    with open(output_file_path, 'w') as file:
        if DEBUG:
            print(f"Saving extracted {source} data...")
        file.write(text)

    return text


def extract_tables_to_csv(csv_file_path, output_path):
    def save_table(table_lines, table_number, output_folder):
        output_file_path = os.path.join(output_folder, f"Table_{table_number}.csv")

        # Check if the first row is empty or contains only commas
        if not any(table_lines[0]) or all(cell == '' for cell in table_lines[0]):
            table_lines = table_lines[1:]  # Remove the first row if it's empty

        with open(output_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(table_lines)
        if DEBUG:
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

def extract_tables_to_dfs(csv_file_path):
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

def nanonets_table_extract(nano_extracted_tables_csv_path, input_file):
    if os.path.exists(nano_extracted_tables_csv_path):
        print("Tables already extracted with Nanonets")
        return

    print("Extracting tables using Nanonets API...")
    model = NANONETSOCR()
    model.set_token(os.getenv("NANONESTS_TABLE_MODEL_TOKEN"))
    model.convert_to_csv(input_file, output_file_name=nano_extracted_tables_csv_path)