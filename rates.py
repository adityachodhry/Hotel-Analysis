import json
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# MongoDB connection
client = MongoClient("mongodb+srv://Retvens:JMdZt2hEPsqHuVQl@r-rate-shopper-cluster.nlstcxk.mongodb.net/")
db = client['ratex']
rateCollections = db['otarates']
verifiedproperties = db['verifiedproperties']

# Custom function to convert MongoDB objects to a serializable format
def serialize_mongo_obj(data):
    if isinstance(data, ObjectId):
        return None  # Exclude ObjectId from serialization
    if isinstance(data, datetime):
        return data.isoformat()
    return data

# Recursively serialize MongoDB documents, excluding "_id"
def serialize_document(document):
    if isinstance(document, dict):
        return {key: serialize_document(value) for key, value in document.items() if key != "_id"}
    elif isinstance(document, list):
        return [serialize_document(item) for item in document]
    else:
        return serialize_mongo_obj(document)

# Fetch data for a specific hId
hId = 53005

# Initialize data structure
all_rates_data = {
    "ourHidRates": [],
    "compsetRates": []
}

# Fetch channel manager details
ratesField = rateCollections.find_one({"hId": hId})

# Fetch OTA rates for ourHid
if ratesField:
    ourHid = ratesField.get('hId')
    print(f"ourHid: {ourHid}")
    rates_ourHid = rateCollections.find({"hId": ourHid})
    all_rates_data["ourHidRates"] = [serialize_document(rate) for rate in rates_ourHid]

# Fetch property details from verifiedproperties
propertyDetail = verifiedproperties.find_one({"hId": hId})

# Fetch OTA rates for compsetIds
if propertyDetail:
    compset = propertyDetail.get('compsetId', [])
    compset_ids = [item['compsetId'] for item in compset if 'compsetId' in item]
    print(f"compsetIds: {compset_ids}")

    for compset_id in compset_ids:
        rates_compset = rateCollections.find({"hId": compset_id})
        all_rates_data["compsetRates"].extend([serialize_document(rate) for rate in rates_compset])

# Save all rates data to JSON
with open("all_rates_data.json", "w") as json_file:
    json.dump(all_rates_data, json_file, indent=4)

# Print combined data for inspection (optional)
# print(json.dumps(all_rates_data, indent=4))
