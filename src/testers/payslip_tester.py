import os, sys
sys.path.append('src/utils')
from src.utils.load_config import LoadConfig
from src.utils.payslip_processor import PayslipProcessor
import tkinter as tk
from tkinter import filedialog

app_config = LoadConfig()


def select_file_and_get_path():
    # Initialize the Tkinter root element
    root = tk.Tk()
    root.withdraw()  # Use to hide the main window

    # Set the starting directory to your data folder path
    # Adjust this path to match the location of your data folder
    initial_dir = app_config.client_data_directory

    # Open the file dialog and let the user select a file
    file_path = filedialog.askopenfilename(initialdir=initial_dir)

    if file_path:
        print(f"Selected file path: {file_path}")
        return file_path
    else:
        print("No file was selected.")
        return None

def main():
    payslip_path = select_file_and_get_path()
    # client_path = os.path.join(app_config.client_data_directory,"Alex and Patricia\Alex")
    # payslip_path = r"N:\Dev\AI\Underwriting\data\clients\Alex and Patricia\Alex\Alexander_Deaibes_Pay_Stub(s)_9tM4WQ8J9J3yc13DgjRkEo.pdf"
    #
    payslip_data = PayslipProcessor(payslip_path)
    print("Regular: " + str(payslip_data.get_earnings('regular' ,agent='csv')))
    print("YTD: " + str(payslip_data.get_earnings('ytd' ,agent='csv')))

if __name__ == "__main__":
    main()

#########
# Notes #
#########
'''
1. AI doesnt know which tables to look at when multiple paystubs are in the same PDF, multiple pages
    1.a. Try a single prompt
    1.b. Split up the pages
    
2
'''