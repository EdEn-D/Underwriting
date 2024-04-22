import json

import requests

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload
import gspread
from oauth2client.service_account import ServiceAccountCredentials
def upload_image_to_drive(image_path, credentials_file):
    # Define the scope
    scopes = ['https://www.googleapis.com/auth/drive.file']
    creds = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    drive_service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': 'MyImage.png'}
    media = MediaFileUpload(image_path, mimetype='image/png')
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='webViewLink').execute()
    return file.get('webViewLink')

# Example usage
SERVICE_ACCOUNT_FILE = r'N:\Dev\AI\Underwriting\single-obelisk-421013-3fc29a09a343.json'
local_image_path = r'N:\Dev\AI\Underwriting\notebooks\cropped.jpg'
image_url = upload_image_to_drive(local_image_path, SERVICE_ACCOUNT_FILE)
print("Uploaded image URL:", image_url)

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
        return data['data']['link']
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


# Usage example
CLIENT_ID = 'd5edbd48187294f'
IMAGE_PATH = r'N:\Dev\AI\Underwriting\notebooks\cropped.jpg'

uploaded_image_url = upload_image_to_imgur(IMAGE_PATH, CLIENT_ID)
if uploaded_image_url:
    print("Uploaded Image URL:", uploaded_image_url)
else:
    print("Failed to upload image.")


def getrow(s):
    for c in s:
        i = 0
        if c.isdigit():
            i = s.index(c)
            return str(s[i:])


def append_image_link_to_sheet(spreadsheet_id, credentials_json, image_url):
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).sheet1  # Open the first sheet

    # Append a new row with an image formula
    image_formula = r"=ADD"
    test = sheet.append_row([image_formula])
    print(json.dumps(test, indent=4))
    updated_cell = test["updates"]["updatedRange"].split("!")[1]
    print(updated_cell)
    # print(sheet.acell(updated_cell).value)
    print(getrow(updated_cell))
    i = int(getrow(updated_cell))
    sheet.update_cell(i, 1, '=ADD(yourmother)')


SPREADSHEET_ID = '1QhAFMUnA3r3AhxnivebHb1BIsYvX2uXiUFumyZz7uRg'
SERVICE_ACCOUNT_FILE = r'N:\Dev\AI\Underwriting\single-obelisk-421013-3fc29a09a343.json'

append_image_link_to_sheet(SPREADSHEET_ID, SERVICE_ACCOUNT_FILE, uploaded_image_url)