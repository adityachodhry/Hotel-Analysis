from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

# MongoDB connection (replace with environment variable)
client = MongoClient(os.getenv('MONGODB_URI', "mongodb+srv://Retvens:JMdZt2hEPsqHuVQl@r-rate-shopper-cluster.nlstcxk.mongodb.net/"))
db = client['ratex']
rateCollections = db['otarates']
verifiedproperties = db['verifiedproperties']

# Helper function to parse the date string
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

@app.route('/get-rates', methods=['GET'])
def get_rates():
    try:
        # Get query parameters: hId, start_date, end_date
        hId = request.args.get('hId')
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        if not hId or not start_date_str or not end_date_str:
            return jsonify({"error": "hId, start_date, and end_date are required"}), 400

        try:
            hId = int(hId)
        except ValueError:
            return jsonify({"error": "hId must be an integer"}), 400

        # Convert the date strings to datetime objects
        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        # Fetch property details and compsetIds
        property_detail = verifiedproperties.find_one({"hId": hId}, {"compsetId": 1})
        compset_ids = [
            item['compsetId'] for item in property_detail.get('compsetId', [])
            if 'compsetId' in item
        ] if property_detail else []

        # Combine hId and compset_ids for a single query
        all_hIds = [hId] + compset_ids

        # Query rates for all hIds within the date range
        query = {
            "hId": {"$in": all_hIds},
            "rates": {
                "$elemMatch": {
                    "checkIn": {"$lte": end_date},
                    "checkOut": {"$gte": start_date}
                }
            }
        }
        projection = {
            "hId": 1,
            "rates.roomID": 1,
            "rates.checkIn": 1,
            "rates.checkOut": 1,
            "rates.roomName": 1,
            "rates.roomPlan": 1,
            "rates.price": 1
        }
        documents = rateCollections.find(query, projection)

        # Process results
        our_rates = []
        compset_rates = []

        for document in documents:
            for rate in document.get('rates', []):
                check_in = rate['checkIn']
                check_out = rate['checkOut']
                # Filter rates within the specific date range
                if start_date <= check_in <= end_date or start_date <= check_out <= end_date:
                    formatted_rate = {
                        "checkIn": check_in.strftime('%Y-%m-%d'),
                        "checkOut": check_out.strftime('%Y-%m-%d'),
                        "roomName": rate.get("roomName"),
                        "roomPlan": rate.get("roomPlan"),
                        "price": rate.get("price")
                    }
                    if document['hId'] == hId:
                        our_rates.append(formatted_rate)
                    else:
                        formatted_rate["compsetHId"] = document['hId']
                        compset_rates.append(formatted_rate)

        # Return combined response
        return jsonify({
            "ourRates": our_rates,
            "compsetRates": compset_rates
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)