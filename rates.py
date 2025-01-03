import json
from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb+srv://Retvens:JMdZt2hEPsqHuVQl@r-rate-shopper-cluster.nlstcxk.mongodb.net/")
db = client['ratex']
rateCollections = db['otarates']
verifiedproperties = db['verifiedproperties']

# Fetch data for a specific hId
hId = 53005

# Fetch channel manager details
ratesField = rateCollections.find_one({"hId": hId})

# Fetch OTA rates for ourHid
if ratesField:
    ourHid = ratesField.get('hId')
    print(f"ourHid: {ourHid}")
    rates_ourHid = rateCollections.find({"hId": ourHid})

# Fetch property details from verifiedproperties
propertyDetail = verifiedproperties.find_one({"hId": hId})

# Fetch OTA rates for compsetIds
if propertyDetail:
    compset = propertyDetail.get('compsetId', [])
    compset_ids = [item['compsetId'] for item in compset if 'compsetId' in item]
    print(f"compsetIds: {compset_ids}")

