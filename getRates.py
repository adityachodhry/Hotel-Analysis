from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from bson import ObjectId


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
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Query MongoDB for documents matching hId
        documents = rateCollections.find({'hId': hId})

        result = []
        for document in documents:
            for rate in document.get('rates', []):
                # Extract and format dates
                check_in = rate['checkIn'] if isinstance(rate['checkIn'], datetime) else rate['checkIn']['$date']
                check_out = rate['checkOut'] if isinstance(rate['checkOut'], datetime) else rate['checkOut']['$date']

                # Filter by date range
                if start_date <= check_in <= end_date:
                    formatted_rate = {
                        "roomID": rate.get("roomID"),
                        "checkIn": check_in.strftime('%Y-%m-%d'),
                        "checkOut": check_out.strftime('%Y-%m-%d'),
                        "roomName": rate.get("roomName"),
                        "roomPlan": rate.get("roomPlan"),
                        "price": rate.get("price")
                    }
                    result.append(formatted_rate)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
