import os
from pyairtable import Api
from pyairtable.utils import attachment
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

api = Api(os.environ['AIRTABLE_API_KEY'])

table = api.table(os.getenv("AIRTABLE_BASE_ID"), os.getenv("AIRTABLE_TABLE_ID"))
# table.all()
# table.create({'Name': 'John Doe', 'Notes': 'Some notes'})

def log_eval_data(data):
    pdf_url = r"https://pentagon69.duckdns.org/s/qqPorMwRw922CgE/download/%D7%94%D7%95%D7%93%D7%A2%D7%94%20%D7%A2%D7%9C%20%D7%AA%D7%90%D7%95%D7%A0%D7%AA%20%D7%93%D7%A8%D7%9B%D7%99%D7%9D.pdf"
    print(attachment(pdf_url))

    # table_data = { **data['data'] , **data['metadata'] , **{'LOE', attachment(table_url)} }
    print("\n\n\n")
    # print({ **data['data'] , **data['metadata'] })
    # table.create( table_data )
    table.create( {'LOE': [attachment(pdf_url)]} )



    