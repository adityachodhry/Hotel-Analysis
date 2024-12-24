from pymongo import MongoClient

# MongoDB connection
client = MongoClient("mongodb+srv://Retvens:JMdZt2hEPsqHuVQl@r-rate-shopper-cluster.nlstcxk.mongodb.net/")
db = client['ratex']
verifiedproperties = db['verifiedproperties']

def getAllProperties(properties):

    # Query with conditions
    query = {"isActive": True, "isRetvens": True}

    # Fetch results and prepare data for JSON
    properties = list(verifiedproperties.find(query, {"hId": 1, "propertyName": 1, "_id": 0}))

    print(properties)

    return properties