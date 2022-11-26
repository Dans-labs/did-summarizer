curl -X 'POST' \
  'http://0.0.0.0:8000/cache' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": ["uri_1", "uri_2", "uri_3"]
}'
