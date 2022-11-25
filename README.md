# did-summarizer
Linked Data summarizer driven by Decentralized Identifiers (DIDs)

Funded by CLARIAH project

# Installation

```
cp .env_sample .env
export traefikhost=somedomain.dans.knaw.nl
cd ./distros/DID
docker-compose up -d
```

# DID names

By default DID containers available for different ontologies:
* persons -> https://persons.did.zandbak.dans.knaw.nl
* locations -> https://locations.did.zandbak.dans.knaw.nl
* organizations -> https://organizations.did.zandbak.dans.knaw.nl
* uri -> https://uri.did.zandbak.dans.knaw.nl

API endpoint with cache and resolver:
* api -> https://api.did.zandbak.dans.knaw.nl

