import requests
import json
  
# defining the api-endpoint 
API_ENDPOINT = "http://0.0.0.0:8000/cache"
API_ENDPOINT = "https://api.zandbak.dans.knaw.nl/cache"
  
# your API key here
API_KEY = "XXXXXXXXXXXXXXXXX"
  
# data to be sent to api
urls = ['url_4','url_5','url_6']
data = {}
data['url'] = urls
print(data)
r = requests.post(url = API_ENDPOINT, data = json.dumps(data))
print(r.text)

data = {}
persons = ["Rutte", "Zelenskyy", "Biden"]
data['url'] = persons
r = requests.post(url = API_ENDPOINT, data = json.dumps(data))
print(r.text)
