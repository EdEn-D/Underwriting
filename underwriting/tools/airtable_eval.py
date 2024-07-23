import os
from pyairtable import Api
from pyairtable.utils import attachment
from dotenv import load_dotenv, find_dotenv
import requests
import xml.etree.ElementTree as ET

load_dotenv(find_dotenv())

NEXTCLOUD_URL = os.getenv("NEXTCLOUD_URL")
NEXTCLOUD_USER = os.getenv("NEXTCLOUD_USER")
NEXTCLOUD_PASSWORD = os.getenv("NEXTCLOUD_PASSWORD")
NEXTCLOUD_TEMP_SUBDIRECTORY = os.getenv("NEXTCLOUD_TEMP_SUBDIRECTORY")
# FILE_PATH = r"N:\Dev\AI\Underwriting\data\clients\Alex and Patricia\Alex\LOE - Alexander_Deaibes_Letter(s)_of_Employment_Confirming_Start_Date,_Position_and_Income_1B8mAwSAYfoChPo.pdf"

api = Api(os.environ['AIRTABLE_API_KEY'])
table = api.table(os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE_ID"))
# table.all()
# table.create({'Name': 'John Doe', 'Notes': 'Some notes'})

# Function to upload a file to Nextcloud
def upload_to_nextcloud(local_file_path):
    remote_file_path = NEXTCLOUD_TEMP_SUBDIRECTORY + os.path.basename(local_file_path)
    # remote_file_name = 'temp/' + remote_file_name
    with open(local_file_path, 'rb') as file:
        response = requests.put(
            NEXTCLOUD_URL + "/remote.php/webdav/" +  remote_file_path,
            data=file,
            auth=(NEXTCLOUD_USER, NEXTCLOUD_PASSWORD)
        )
    if response.status_code == 201:
        return remote_file_path
    else:
        raise Exception('Failed to upload file to Nextcloud')


def get_nextcloud_public_link(remote_path):
    """Create a public link for the file on Nextcloud and return it."""
    response = requests.post(
        f"{NEXTCLOUD_URL}/ocs/v2.php/apps/files_sharing/api/v1/shares",
        auth=(NEXTCLOUD_USER, NEXTCLOUD_PASSWORD),
        headers={'OCS-APIRequest': 'true'},
        data={
            'path': remote_path,
            'shareType': 3,  # Public link
            'permissions=1': 3,  # Public link TODO: Fix this?
        }
    )
    if response.status_code == 200:
        try:
            # Parse the XML response
            root = ET.fromstring(response.content)
            # Find the URL in the XML
            url = root.find('.//url').text
            return url
        except ET.ParseError as e:
            raise Exception(f"Failed to parse XML response: {e}")
        except AttributeError as e:
            raise Exception(f"Failed to find URL in XML response: {e}")
    else:
        raise Exception(f"Failed to create public link: {response.status_code} - {response.text}")


# OLD - Function to upload LOE to Airtable with all fields seperated
# def upload_to_airtable(data, file_url):
#     table_data = { **data['data'] , **data['metadata'] , **{'LOE': [attachment(file_url)]} }
#     table.create( table_data )

def upload_to_airtable(data, file_url):
    # TODO: append to table
    '''
    formula = f"{{client_name}}='Alexander Deaibes'"
    records = table.all(formula=formula)
    table.update(records[0]['id'], {'paystub_data' : 'test'})
    '''
    client_name = data[list(data.keys())[0]]['data']['client_name']
    formatted_data = {list(data.keys())[0] : str(data[list(data.keys())[0]])}
    table_data = { **{'client_name' : client_name}, **formatted_data, **{'file': [attachment(file_url)]} }
    print(table_data)
    table.create( table_data )

def delete_from_nextcloud(remote_path):
    """Delete the file from Nextcloud."""
    response = requests.delete(
            NEXTCLOUD_URL + "/remote.php/webdav/" +  remote_path,
            auth=(NEXTCLOUD_USER, NEXTCLOUD_PASSWORD)
        )
    
    if response.status_code != 204:
        raise Exception(f"Failed to delete file: {response.status_code}")
    

def create_airtable_log(data, file_path):
    # print(list(data.keys())[0])
    try:
        upload_path = upload_to_nextcloud(file_path)
        link = get_nextcloud_public_link(upload_path)
        direct_link = link + '/download'
        upload_to_airtable(data, direct_link)
    finally:
        delete_from_nextcloud(upload_path)
