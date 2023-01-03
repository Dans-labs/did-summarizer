#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Developed by Slava Tykhonov
# Data Archiving and Networked Services (DANS-KNAW), Netherlands
import uvicorn
import requests
import re
import os
import json
import urllib3, io
import pandas as pd
import redis
import subprocess
import json
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from starlette.responses import FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from utils import connectmongo, storekey, create_did, rebuildcache, S3connect, S3buckets
from Namespaces import NameSpaces
from pydantic import BaseModel
import arrow

class Archive(BaseModel):
    did: Optional[str] = None
    content:  Optional[str] = None
    url:  Optional[str] = None
    filename: Optional[str] = None
    author: Optional[str] = None

class Item(BaseModel):
    text: str

rcache = redis.Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=os.environ['REDIS_DB'])
rcacheper = redis.Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=os.environ['REDIS_PER'])
rcacheloc = redis.Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=os.environ['REDIS_LOC'])
rcacheorg = redis.Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=os.environ['REDIS_ORG'])
collection = connectmongo()
rebuildcache(rcache, collection['uri'])
DEBUG = os.environ['DEBUG']

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="CLARIAH Linked Data Summarizer",
        description="Service to support Linked Open Data tasks.",
        version="0.1",
        routes=app.routes,
    )

    openapi_schema['tags'] = tags_metadata

    app.openapi_schema = openapi_schema
    return app.openapi_schema

tags_metadata = [
    {
        "name": "country",
        "externalDocs": {
            "description": "Put this citation in working papers and published papers that use this dataset.",
            "authors": 'Slava Tykhonov',
            "url": "https://dans.knaw.nl/en",
        },
    },
    {
        "name": "namespace",
        "externalDocs": {
            "description": "API endpoint for specific tasks.",
            "authors": 'Slava Tykhonov',
            "url": "https://dans.knaw.nl",
        },
    }
]

app = FastAPI(
    openapi_tags=tags_metadata
)

class Item(BaseModel):
    name: str
    content: Optional[str] = None

templates = Jinja2Templates(directory='templates/')
app.mount('/static', StaticFiles(directory='static'), name='static')

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.openapi = custom_openapi
configfile = '/app/conf/gateway.xml'
if 'config' in os.environ:
    configfile = os.environ['config']
http = urllib3.PoolManager()

@app.get("/")
async def home():
    return "CLARIAH Vocabulary Summarizer v.0.1 https://github.com/Dans-labs/did-summarizer"

@app.get("/cache")
async def cache(uri: str, token: Optional[str] = None):
    params = []
    did = False
    if rcache.exists(uri):
        return rcache.mget(uri)[0]
    else:
        return create_did(rcache, uri, collection)
    return did

@app.post("/cache")
async def root(info : Request):
    data = await info.json()
    if 'url' in data:
        urls = {}
        for url in data['url']:
            if rcache.exists(url):
                urls[url] = rcache.mget(url)[0]
            else:
                urls[url] = create_did(rcache, url, collection)
        return urls
    return {"message": f"You wrote: %s" % str(data)}

from Namespaces import NameSpaces

@app.get("/summarizer")
async def summarizer(url: str, token: Optional[str] = None, persist: Optional[str] = None):
    ns = NameSpaces(url)
    data = {}
    data['statements'] = ns.getstatements()
    data['prefixes'] = ns.getnamespaces()
    data['stats'] = ns.getstats()
    if persist:
        if 'stats' in data:
            urls = {}
            utc = arrow.utcnow()
            local = utc.to(os.environ['TIMEZONE'])
            data['date'] = local.format('YYYY-MM-DD HH:mm:ss ZZ')
            data['timezone'] = os.environ['TIMEZONE']
            metadata = { 'uri': url, 'statistics': data}
            if rcache.exists(url):
                urls[url] = rcache.mget(url)[0]
            else:
                urls[url] = create_did(rcache, url, collection, metadata)
            data['did'] = urls[url]
    return data

@app.get("/recommend")
async def recommend(searchTerm: str, searchClass: Optional[str] = None, endpoint: Optional[str] = None):
    cmd = "yarn --cwd /app/vocabulary-recommender recommend -t \'%s\' -f json" % searchTerm
    if searchClass:
        cmd = "%s -c %s" % (cmd, searchClass)
    if endpoint:
        cmd = "%s -e %s" % (cmd, endpoint)
    task = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    data = task.stdout.read().decode("utf-8").split('\n')
    assert task.wait() == 0
    data = data[2:]
    data = data[:-2]
    if data:
        #json.dumps(json.loads(' '.join(data))))
        d = json.dumps(json.loads(' '.join(data)), indent=4, default=str)
        return Response(content=d, media_type="application/json")
    return False

@app.get("/archive")
async def getfromstorage(did: str):
    if did:
        conn = S3connect()
        bucket = False
        for thisbucket in conn.get_all_buckets():
            if thisbucket.name == os.environ['S3_DEFAULT_BUCKET']:
                bucket = thisbucket
        key = bucket.get_key(did)
        return str(key.get_contents_as_string()).split('\n') 

@app.post("/archive")
async def storage(archive: Archive):
    if archive.did:
        conn = S3connect()
        bucket = False
        for thisbucket in conn.get_all_buckets():
            if thisbucket.name == os.environ['S3_DEFAULT_BUCKET']:
                bucket = thisbucket

        if not bucket:
            try:
                bucket = conn.create_bucket(os.environ['S3_DEFAULT_BUCKET'])
            except:
                skip = True
        key = bucket.new_key(archive.did)
        if archive.content:
            key.set_contents_from_string(archive.content)
        if archive.url:
            key.set_contents_from_string(requests.get(archive.url).text)
        return True
    return False

@app.get('/version')
def version():
    return '0.1'

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9266)
