"""
Author: shihan
Date: 2023-12-07 22:20:22
version: 1.0
description: 
"""
import requests

# https://api.ebay.com/buy/browse/v1/item_summary/search?q=drone&limit=3

url = "https://api.ebay.com/buy/browse/v1/item_summary/search?q=drone&limit=3"

response = requests.get(url)
# Check the status code
if response.status_code == 200:
    print("Request was successful!")
    print("Status code:", response.status_code)
    print(response)
else:
    print("Request failed!")
    print("Status code:", response.status_code)
