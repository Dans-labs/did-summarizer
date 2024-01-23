from pymongo import MongoClient
import os
import redis
import json
import requests
import boto 
import boto.s3.connection
import boto3

DEBUG = False
if 'DEBUG' in os.environ:
    DEBUG = os.environ['DEBUG']

def connectmongo():
    client = MongoClient(os.environ['MONGO_HOST'], int(os.environ['MONGO_PORT']))
    db = client[os.environ['MONGO_DB']]
    collections = {}
    collections['keys'] = db[os.environ['MONGO_COLLECTION']]
    collections['uri'] = db[os.environ['MONGO_URI']]
    return collections

def storekey(coll, thisdoc):
    #doc1 = {"name": "Ram", "age": "26", "city": "Hyderabad"}
    coll.insert_one(thisdoc)
    return

def rebuildcache(rcache, coll):
    cursor = coll.find({})
    for document in cursor:
          rcache.mset({ document['uri']: document['did']})
    return

def getmongocache(rcache, coll):
    cursor = coll.find({})
    data = []
    for document in cursor:
          data.append({ document['uri']: document['did']})
    return

def create_payload(metadata, uri):
    data = {}
    context = {}
    context['@context'] = uri
    context['metadata'] = metadata
    context['authentication'] = []
    context['service'] = []
    data['didDocument'] = context
    data['secret'] = { "doc_pwd": os.environ['DID_PWD'], "rev_pwd": os.environ['DID_SECRET'] }
    return json.dumps(data)

def return_did(uri, metadata=None):
    did = False
    if uri:
        metadata = { 'uri': uri }
        payload = str(create_payload(metadata, uri))
        if 'traefikhost' in os.environ:
            DID_url = "%s/%s" % (os.environ['GENERICURI_DID_ALIAS'], "1.0/create?method=oyd")
        else:
            DID_url = "%s/%s" % (os.environ['GENERICURI_DID'], "1.0/create?method=oyd")
        if DEBUG:
            print(DID_url)
            print(payload)
        r = requests.post(DID_url, data=payload, headers=headers)
        print(r.json())
        did = str(r.json()["didState"]["did"])
        if DEBUG:
            print("DID: %s" % did)
        rcache.mset({uri: did})
    return did

def create_did(rcache, uri, collection, metadata=None):
    if uri:
        headers = {'content-type': 'application/json'}
        if not metadata:
            metadata = { 'uri': uri }
        payload = str(create_payload(metadata, uri))
        if 'traefikhost' in os.environ:
            DID_url = "%s/%s" % (os.environ['GENERICURI_DID_ALIAS'], "1.0/create?method=oyd")
        else:
            DID_url = "%s/%s" % (os.environ['GENERICURI_DID'], "1.0/create?method=oyd")
        if DEBUG:
            print(DID_url)
            print(payload)
        r = requests.post(DID_url, data=payload, headers=headers)
        print(r.json())
        didresponse = r.json()
        did = str(r.json()["didState"]["did"])
        doc = {}
        doc[did] = didresponse
        storekey(collection['keys'], doc)
        rdoc = {}
        rdoc['uri'] = uri
        rdoc['did'] = did
        storekey(collection['uri'], rdoc)
        if DEBUG:
            print("DID: %s" % did)
        rcache.mset({uri: did})
        return did
    return

def S3connect():
    if is_s3_ssl_connection():
        conn = boto.connect_s3(
        aws_access_key_id = os.environ['S3_ACCESS_KEY'],
        aws_secret_access_key = os.environ['S3_SECRET_KEY'],
        host = os.environ['S3_API_HOST'],
        #is_secure=False,               # uncomment if you are not using ssl
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
        )
        return conn
    else:
        conn = boto3.resource('s3', endpoint_url=os.environ['S3_API_HOST'], aws_access_key_id=os.environ['S3_ACCESS_KEY'], aws_secret_access_key=os.environ['S3_SECRET_KEY'])
        return conn
    return False

def is_s3_ssl_connection():
    if 'http://' in os.environ['S3_API_HOST']:
        return False
    return True


def S3buckets(conn):
    buckets = []
    if is_s3_ssl_connection():
        for bucket in conn.get_all_buckets():
            buckets.append({'name': bucket.name, 'date': bucket.creation_date })
    else:
        for bucket in conn.buckets.all():
            buckets.append({'name': bucket.name})
    return buckets
