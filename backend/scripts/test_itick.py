import requests

url = "https://api.itick.org/symbol/list?type=stock&region=hk&code=6166"

headers = {
    "accept": "application/json",  # ← comma added here
    "token": "5a2f0db93cf94ecf9f2019a06ac63cdb3812a741ed7c4e248335549855ab6766"
}

response = requests.get(url, headers=headers)

print(response.text)