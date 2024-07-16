import os, sys
sys.path.append('src/utils')
from src.utils.load_config import LoadConfig
from src.utils.payslip_processor import PayslipProcessor
import tkinter as tk
from tkinter import filedialog
from colorama import Fore, Back, Style
import testing_tools

app_config = LoadConfig()


def select_file_and_get_path(window_title, initial_dir=app_config.client_data_directory):
    # Initialize the Tkinter root element
    root = tk.Tk()
    root.withdraw()  # Use to hide the main window

    # Set the window title
    root.title(window_title)

    # Open the file dialog and let the user select a file
    file_path = filedialog.askopenfilename(title=window_title , initialdir=initial_dir)

    if file_path:
        print(f"Selected file path: {file_path}")
        return file_path
    else:
        # print("No file was selected.")
        raise FileExistsError("File not selected")

def main():
    # loe_path = select_file_and_get_path("Select LOE file")
    payslip_path = select_file_and_get_path("Select payslip file")# , os.path.dirname(loe_path))

    payslip_data = PayslipProcessor(payslip_path)

    regular_earnings = payslip_data.get_earnings('regular', agent='csv')
    ytd_earnings = payslip_data.get_earnings('ytd', agent='csv')
    dates_text = payslip_data.get_payslip_dates(source='txt')
    dates_ocr = payslip_data.get_payslip_dates(source='ocr')
    dates_csv = payslip_data.get_payslip_dates_csv()

    data = {}
    data["payslip_path"] = payslip_path
    data["filename"] = os.path.basename(payslip_path)
    data["regular_earnings"] = regular_earnings
    data["ytd_earnings"] = ytd_earnings
    data["dates_text"] = dates_text
    data["dates_ocr"] = dates_ocr
    data["dates_csv"] = dates_csv

    testing_tools.log_to_eval_sheet(payslip_path, data)

    print(Back.BLUE + "Regular: " + regular_earnings)
    print(Back.BLUE + "YTD: " + ytd_earnings)
    print(Back.BLUE + "Dates from text: " + dates_text)
    print(Back.BLUE + "Dates from ocr: " + dates_ocr)
    print(Back.BLUE + "Dates from csv: " +  dates_csv)

if __name__ == "__main__":
    main()

#########
# Notes #
#########
'''
1. AI doesnt know which tables to look at when multiple paystubs are in the same PDF, multiple pages
    1.a. Try a single prompt
    1.b. Split up the pages

2. Dates need more work  
'''