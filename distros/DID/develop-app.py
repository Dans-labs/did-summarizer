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
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from starlette.responses import FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

rcache = redis.Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=os.environ['REDIS_DB'])
rcacheper = redis.Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=os.environ['REDIS_PER'])
rcacheloc = redis.Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=os.environ['REDIS_LOC'])
rcacheorg = redis.Redis(host=os.environ['REDIS_HOST'], port=os.environ['REDIS_PORT'], db=os.environ['REDIS_ORG'])
headers = {'content-type': 'application/json'}
DEBUG = os.environ['DEBUG']

class Item(BaseModel):
    text: str

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

@app.get("/cache")
async def cache(uri: str, token: Optional[str] = None):
    params = []
    did = False
    if rcache.exists(uri):
        return rcache.mget(uri)[0]
    else:
        metadata = { 'uri': uri }
        payload = str(create_payload(metadata, uri))
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
    return did

@app.post("/cache")
async def root(info : Request):
    data = await info.json()
    return {"message": f"You wrote: %s" % str(data)}

@app.get('/version')
def version():
    return '0.1'

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9266)
