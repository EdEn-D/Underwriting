import os
from pyairtable import Api
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

api = Api(os.environ['AIRTABLE_API_KEY'])
table = api.table('applXBPhmmGM2XGhN', 'tblBigclL3dSrrEnQ')
table.all()
table.create({'Name': 'John Doe', 'Notes': 'Some notes'})