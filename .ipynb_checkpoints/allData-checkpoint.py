import json
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Custom function to convert MongoDB objects to a serializable format
def serialize_mongo_obj(data):
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, datetime):
        return data.isoformat()
    return data

# Recursively serialize MongoDB documents
def serialize_document(document):
    if isinstance(document, dict):
        return {key: serialize_document(value) for key, value in document.items()}
    elif isinstance(document, list):
        return [serialize_document(item) for item in document]
    else:
        return serialize_mongo_obj(document)

# Custom JSON encoder
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# MongoDB connection
client = MongoClient("mongodb+srv://Retvens:JMdZt2hEPsqHuVQl@r-rate-shopper-cluster.nlstcxk.mongodb.net/")
db = client['ratex']
collection = db['channelmanagers']
rCollections = db['reservations']
rateCollections = db['otarates']
verifiedproperties = db['verifiedproperties']

# Fetch data for a specific hId
hId = 20079

# Initialize data structure
all_reservations_data = []

# Fetch channel manager details
channel = collection.find_one({"hId": hId})
if channel:
    property_code = channel.get('channelManagerHotelId')

    if property_code:
        reservations = rCollections.find({"hotelCode": property_code})
        
        # Initialize a dictionary to group reservations by hotelCode
hotel_reservations = {}

# Iterate through the reservations and organize data
for allReservations in reservations:
    hotelCode = allReservations.get('hotelCode')

    # Initialize the structure for a new hotelCode
    if hotelCode not in hotel_reservations:
        hotel_reservations[hotelCode] = {"hotelCode": hotelCode, "reservations": []}

    # Extract required fields for each reservation
    reservation_data = {
        "reservationNumber": allReservations.get('reservationNumber'),
        "source": allReservations.get('source'),
        "sourceSegment": allReservations.get('sourceSegment'),
        "arrivalDate": allReservations.get('bookingDetails', {}).get('arrivalDate'),
        "departureDate": allReservations.get('bookingDetails', {}).get('departureDate'),
        "totalNights": allReservations.get('bookingDetails', {}).get('totalNights'),
        "currentStatus": allReservations.get('bookingDetails', {}).get('currentStatus'),
        "roomTypeId": allReservations.get('bookingDetails', {}).get('roomDetails', {}).get('roomTypeId'),
        "roomTypeName": allReservations.get('bookingDetails', {}).get('roomDetails', {}).get('roomTypeName'),
        "roomPlan": allReservations.get('bookingDetails', {}).get('roomDetails', {}).get('roomPlan'),
        "totalAdults": allReservations.get('bookingDetails', {}).get('roomDetails', {}).get('pax', {}).get('totalAdults'),
        "totalChildren": allReservations.get('bookingDetails', {}).get('roomDetails', {}).get('pax', {}).get('totalChildren'),
        "status": allReservations.get('paymentDetails', {}).get('status'),
        "amount": allReservations.get('paymentDetails', {}).get('amount'),
        "roomCost": allReservations.get('priceSummary', {}).get('roomCost'),
        "totalCost": allReservations.get('priceSummary', {}).get('totalCost'),
        "commissionAmount": allReservations.get('priceSummary', {}).get('commissionAmount'),
        "taxAmount": allReservations.get('priceSummary', {}).get('taxAmount'),
    }

    # Add the reservation to the corresponding hotel's reservations list
    hotel_reservations[hotelCode]["reservations"].append(reservation_data)

# Convert the dictionary to a list for saving as JSON
all_reservations_data = list(hotel_reservations.values())

# Save the extracted data into a new JSON file
with open("reservations.json", "w") as json_file:
    json.dump(all_reservations_data, json_file, indent=4, cls=CustomJSONEncoder)

print("Reservations data saved to 'reservations.json'.")


# # Fetch OTA rates for ourHid
# if ratesFiedl:
#     ourHid = ratesFiedl.get('hId')
#     print(f"ourHid: {ourHid}")
#     rates_ourHid = rateCollections.find({"hId": ourHid})
#     all_rates_data["ourHidRates"] = [serialize_document(rate) for rate in rates_ourHid]

# # Fetch OTA rates for compsetIds
# if propertyDetail:
#     compset = propertyDetail.get('compsetId', [])
#     compset_ids = [item['compsetId'] for item in compset if 'compsetId' in item]
#     print(f"compsetIds: {compset_ids}")

#     for compset_id in compset_ids:
#         rates_compset = rateCollections.find({"hId": compset_id})
#         all_rates_data["compsetRates"].extend([serialize_document(rate) for rate in rates_compset])

# # Save all rates data to JSON
# with open("all_rates_data.json", "w") as json_file:
#     json.dump(all_rates_data, json_file, indent=4)

# # Print combined data for inspection
# print(json.dumps(all_rates_data, indent=4))