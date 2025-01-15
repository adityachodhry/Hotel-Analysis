from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI', "mongodb+srv://Retvens:JMdZt2hEPsqHuVQl@r-rate-shopper-cluster.nlstcxk.mongodb.net/"))
db = client['ratex']
rCollections = db['reservations']

# Helper function to parse the date string
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")

@app.route('/get-specific-reservations', methods=['POST'])
def get_specific_reservations():
    try:
        # Parse the JSON payload
        data = request.get_json()
        hotel_code = data.get('hotelCode')
        booking_date_str = data.get('bookingDate')

        # Validate required fields
        if not hotel_code or not booking_date_str:
            return jsonify({"error": "hotelCode and bookingDate are required"}), 400

        # Parse the booking date
        booking_date = parse_date(booking_date_str)

        # Query the database for reservations matching the hotelCode and bookingDate
        query = {
            "hotelCode": hotel_code,
            "bookingDetails.createdOn": {
                "$gte": booking_date,
                "$lt": booking_date + timedelta(days=1)  # Match the entire day
            }
        }

        reservations = rCollections.find(query)

        # Extract specific fields from each reservation
        extracted_reservations = []
        for allReservations in reservations:
            reservation_data = {
                "reservationNumber": allReservations.get('reservationNumber'),
                "source": allReservations.get('source'),
                "sourceSegment": allReservations.get('sourceSegment'),
                "bookingDate": allReservations.get('bookingDetails', {}).get('createdOn'),
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
                "taxAmount": allReservations.get('priceSummary', {}).get('taxAmount')
            }
            extracted_reservations.append(reservation_data)

        # Return the reservations in the response
        return jsonify({
            "status": "success",
            "data": extracted_reservations
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)