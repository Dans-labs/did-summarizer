import requests
res = requests.post('http://localhost:8000/cache',
    headers = {
        'Content-type': 'application/json'
    },
    json = {"https://api.zandbak.dans.knaw.nl/123": "URI"},
)
#print(res.headers['content-type'])
print(res.text)
