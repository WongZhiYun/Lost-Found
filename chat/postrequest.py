import requests
import json

url = "https://httpbin.org/post"
data = {
    'name':'ScrapeOps',
    'title': 'Python Webscraping Playbook',
    'url':'scrapeops.io/python-websraping-playbook'
}

json_data = json.dumps(data)

headers = {'Content-Type':'application/json'}

response = requests.post(url, data=json_data, headers=headers)

print(response.text)