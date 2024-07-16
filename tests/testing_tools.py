import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pdf2image import convert_from_path
import json

# Path to your service account key file
SERVICE_ACCOUNT_FILE = r'N:\Dev\AI\Underwriting\single-obelisk-421013-3fc29a09a343.json'
# Spreadsheet ID from your URL
SPREADSHEET_ID = os.getenv("EVAL_SPREADSHEET_ID")
CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")

# Define the scope
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Authorize with the Google Drive API
creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # Open the first sheet

# Sheet config
IMG_COL = '1'
DATA_COL = '2'


def test_spreadsheet_access():
    # Attempt to open the spreadsheet
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        print("Successfully accessed the spreadsheet!")
        print(sheet.get('A1'))  # Try to read cell A1 as a test
    except gspread.SpreadsheetNotFound:
        raise Exception("Failed to find the spreadsheet. Check the spreadsheet ID and sharing settings.")
    except Exception as e:
        raise Exception("An error occurred:", e)


def convert_pdf_to_images(pdf_path):
    # Extract the directory path and file base from the PDF path
    directory, filename = os.path.split(pdf_path)
    file_base = os.path.splitext(filename)[0]

    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)

    image_paths = []
    # Save each page as an image
    for i, image in enumerate(images):
        image_path = os.path.join(directory, f"{file_base}_page_{i + 1}.png")
        image.save(image_path, 'PNG')
        print(f"Saved: {image_path}")
        image_paths.append(str(image_path))

    return image_paths


import requests


def upload_image_to_imgur(image_path, client_id):
    """
    Uploads an image to Imgur and returns the link to the uploaded image.

    :param image_path: Path to the image file to upload
    :param client_id: Imgur application client ID
    :return: URL of the uploaded image or None if upload fails
    """
    headers = {'Authorization': f'Client-ID {client_id}'}
    url = 'https://api.imgur.com/3/image'

    try:
        with open(image_path, 'rb') as img:
            files = {'image': img}
            response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        data = response.json()
        # print(data)
        return data['data']['link']
    except requests.exceptions.RequestException as e:
        raise Exception(f"An error occurred: {e}")
        # return None


def getrow(s):
    for c in s:
        i = 0
        if c.isdigit():
            i = s.index(c)
            return int(str(s[i:]))

def append_image_link_to_sheet(image_url):
    # scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_json, scope)
    # client = gspread.authorize(creds)

    # Append a new row with an image formula
    image_formula = r"=ADD"
    test = sheet.append_row([image_formula])
    # print(json.dumps(test, indent=4))
    updated_cell = test["updates"]["updatedRange"].split("!")[1]
    print(f"Inserted image to cell: {updated_cell}")
    i = int(getrow(updated_cell))
    sheet.update_cell(i,1, f'=IMAGE("{image_url}"), 4, 600*1.41, 600)')
    return updated_cell


def append_image_to_sheet(pdf_path):
    # pdf_pages = convert_pdf_to_images(r"N:\Dev\AI\Underwriting\data\clients\Safia Seyed\Safia Seyed Paystub.pdf")
    pdf_pages = convert_pdf_to_images(pdf_path)

    pdf_image_path = pdf_pages[0]

    uploaded_image_url = upload_image_to_imgur(pdf_image_path, CLIENT_ID)
    if uploaded_image_url:
        print("Uploaded Image URL:", uploaded_image_url)
    else:
        raise Exception("Failed to upload image.")

    image_cell = append_image_link_to_sheet(uploaded_image_url)
    return image_cell

def log_to_eval_sheet(pdf_path, extracted_data):
    image_cell = append_image_to_sheet(pdf_path)
    row = getrow(image_cell)
    data = json.dumps(extracted_data, indent=4)
    sheet.update_cell(row,2, data)