# import requests, pprint
#
# url = 'https://app.nanonets.com/api/v2/OCR/Model/f77ab717-0ac4-4091-bd97-8f636e96bff2/LabelFile/?async=false'
#
# data = {'file': open('data/clients/Yash Patel/Yash Paystub Nov 17 2023.pdf', 'rb')}
#
# response = requests.post(url, auth=requests.auth.HTTPBasicAuth('39423a53-da18-11ee-8150-fe728a611e82', ''), files=data)
#
# pprint.pprint(response.text)

# Initialise
from nanonets import NANONETSOCR
import json
model = NANONETSOCR()


# Authenticate
# This software is perpetually free :)
# You can get your free API key (with unlimited requests) by creating a free account on https://app.nanonets.com/#/keys?utm_source=wrapper.
model.set_token('39423a53-da18-11ee-8150-fe728a611e82')

# input_file = 'data/clients/Yash Patel/Yash Paystub Nov 17 2023.pdf'
input_file = 'N:/Dev/AI/Underwriting/data/clients/Hemat and Amy/Hemant/Hemant Sud 2021 T4.pdf'
output_file = 'N:/Dev/AI/Underwriting/output2.csv'
model.convert_to_csv(input_file, output_file_name=output_file)