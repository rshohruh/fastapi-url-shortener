import requests
from pprint import pprint
url = "http://127.0.0.1:8000/shorten"
data = {"url": "https://robocontest.uz"}
response = requests.post(url, json=data)

print(response.status_code)
pprint(response.json())
# print(response.reason)