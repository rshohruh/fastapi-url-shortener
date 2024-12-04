import requests
from pprint import pprint
url = "http://127.0.0.1:8000/shorten"
data = {
    "url": "https://robocontest.uz/olympiads/join-via-link?secret=i2e1Xb0QwY7LOmS6jwOJEtxRqwRZQ89Y1733251461&signature=53a91c00d5f45cb9d7e36492ac9935ecbf169022ee0934e90bd21b54de3b246a",
    "vip_url": "abe"
}
response = requests.post(url, json=data)

print(response.status_code)
pprint(response.json())

another_data = {
    "url": "https://google.com"
}

response = requests.post(url, json=another_data)

print(response.status_code)
pprint(response.json())
# print(response.reason)