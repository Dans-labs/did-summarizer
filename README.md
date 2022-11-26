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
* api -> https://api.did.zandbak.dans.knaw.nl/docs

# Cache and storage

All concepts are being cached in RAM using Redis framework and preserved in MongoDB database. After every restart the key:value pair for URI:DID reindexed and available for lookup in the cache. It should be possible to move all DIDs data from one network to another without too much efforts.  

# Use cases

The idea of DID summarizer is to assign unique globally resolvable decentralized identifier DID to any string, particulary to URLs and URIs. 
Possible usage:
* Storing all inbound and outbound links for the specific web page defined by URL
* Assign DIDs for any content and archive it in the decentralized network with access by private key 
* Build sustainable knowledge graph compliant with FAIR principles: every edge and vertice should have their own unique DID identifier 
