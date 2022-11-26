from pymongo import MongoClient
import os
# from utils import connectmongo, storekey

def connectmongo():
    client = MongoClient(os.environ['MONGO_HOST'], int(os.environ['MONGO_PORT']))
    db = client[os.environ['MONGO_DB']]
    coll = db[os.environ['MONGO_COLLECTION']]
    return coll

def storekey(coll, thisdoc):
    #doc1 = {"name": "Ram", "age": "26", "city": "Hyderabad"}
    coll.insert_one(thisdoc)
    return

