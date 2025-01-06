import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
from chat import chatbot_response
import requests
import datetime

# MongoDB connection
client = MongoClient("mongodb+srv://Retvens:JMdZt2hEPsqHuVQl@r-rate-shopper-cluster.nlstcxk.mongodb.net/")
db = client['ratex']
verifiedproperties = db['verifiedproperties']

def getAllProperties():
    # Query with conditions
    query = {"isActive": True, "isRetvens": True}
    # Fetch results and prepare data
    properties = list(verifiedproperties.find(query, {"hId": 1, "propertyName": 1, "_id": 0}))
    return properties

def fetch_rates(hId, start_date, end_date):
    """
    Fetch rates for a given date range using the getRates API.
    Args:
        hId (int): Hotel ID for which rates are to be fetched.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
    Returns:
        dict: Parsed JSON response from the API.
    """
    api_url = "http://127.0.0.1:5000/get-rates"  # Replace with deployed URL
    params = {"hId": hId, "start_date": start_date, "end_date": end_date}

    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API returned status code {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# Streamlit page configuration
st.set_page_config(page_title="Hotel Analysis Tool", layout="wide")

# App Title
st.title("Hotel Analysis Tool")

# Sidebar: Navigation
st.sidebar.header("Retvens Technologies")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Chat With Me"]
)

if page == "Home":
    # Home page content
    st.header("Welcome to the Hotel Analysis Tool")
    st.write(
        """
        This tool provides advanced analytics for the hospitality industry:
        - **Revenue Forecasting**: Analyze and forecast the revenue of your property.
        - **Price Prediction**: Predict future hotel prices using AI-driven models.
        
        Empowering  
        Owners To Become Hoteliers With solutions that make your life easy..
        """
    )

else:
    # Chat With Me Page Content
    st.header("Chat With Me")
    st.write("Ask me anything about the hospitality industry, and I'll provide insights!")

    # Search field
    search_query = st.sidebar.text_input("Search Property", "")

    # Fetch property list from MongoDB
    properties = getAllProperties()

    if properties:
        # Prepare dropdown options
        property_options = [prop["propertyName"] for prop in properties]

        # Filter dropdown based on search query
        filtered_options = [opt for opt in property_options if search_query.lower() in opt.lower()]

        # Dropdown for property selection
        selected_property = st.sidebar.selectbox("Choose a Property", filtered_options)

        if selected_property:
            # Fetch hId for the selected property
            hId = next(prop['hId'] for prop in properties if prop['propertyName'] == selected_property)

            # Display selected property
            st.subheader(f"Selected Property: {selected_property}")

            # Chatbot interaction
            user_input = st.text_input("Type your question here:", placeholder="e.g., Show rates for next 10 days.")
            if user_input:
                response, extra = chatbot_response(user_input, selected_property=selected_property)
                st.subheader("Chatbot Response")
                st.write(response)

                if extra.get("fetch_rates"):
                    # Extract date range from user input
                    today = datetime.date.today()
                    if "next 10 days" in user_input.lower():
                        start_date = today.strftime('%Y-%m-%d')
                        end_date = (today + datetime.timedelta(days=10)).strftime('%Y-%m-%d')
                    elif "next 30 days" in user_input.lower():
                        start_date = today.strftime('%Y-%m-%d')
                        end_date = (today + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
                    elif "past 20 days" in user_input.lower():
                        start_date = (today - datetime.timedelta(days=20)).strftime('%Y-%m-%d')
                        end_date = today.strftime('%Y-%m-%d')
                    else:
                        start_date = today.strftime('%Y-%m-%d')
                        end_date = (today + datetime.timedelta(days=10)).strftime('%Y-%m-%d')

                    # Fetch rates for the selected property
                    rates = fetch_rates(hId, start_date, end_date)
                    if "error" in rates:
                        st.error(rates["error"])
                    else:
                        # Separate our rates and compset rates
                        our_rates = rates.get("ourRates", [])
                        compset_rates = rates.get("compsetRates", [])

                        # Display our rates with room name and room plan filters
                        if our_rates:
                            st.subheader("Our Rates")
                            our_rates_df = pd.DataFrame(our_rates)

                            # Add 'dates' column
                            all_dates = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()

                            # Create a new column 'dates' for all rows
                            dates_expanded = []
                            for _, row in our_rates_df.iterrows():
                                check_in = datetime.datetime.strptime(row['checkIn'], '%Y-%m-%d').date()
                                check_out = datetime.datetime.strptime(row['checkOut'], '%Y-%m-%d').date()
                                
                                # Loop through each date in the range and create corresponding rows
                                dates_expanded.extend([check_in + datetime.timedelta(days=i) for i in range((check_out - check_in).days)])

                            # Add dates column
                            our_rates_df['dates'] = dates_expanded

                            # Remove 'checkIn' and 'checkOut' columns
                            our_rates_df = our_rates_df.drop(columns=['checkIn', 'checkOut'])

                            # Reorder columns to make 'dates' the first column
                            our_rates_df = our_rates_df[['dates'] + [col for col in our_rates_df.columns if col != 'dates']]

                            # Dropdown filters for roomName and roomPlan
                            room_names = our_rates_df['roomName'].unique()
                            room_plans = our_rates_df['roomPlan'].unique()

                            selected_room_name = st.selectbox("Select Room Name", room_names, key="room_name")
                            selected_room_plan = st.selectbox("Select Room Plan", room_plans, key="room_plan")

                            # Filter data based on selections
                            filtered_our_rates = our_rates_df[
                                (our_rates_df['roomName'] == selected_room_name) &
                                (our_rates_df['roomPlan'] == selected_room_plan)
                            ]

                            st.dataframe(filtered_our_rates)

                        # Display compset rates grouped by compsetHId
                        if compset_rates:
                            st.subheader("Compset Rates")
                            compset_rates_df = pd.DataFrame(compset_rates)

                            # Add 'dates' column to compset rates
                            all_dates = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()

                            # Create a new column 'dates' for all rows
                            compset_dates_expanded = []
                            for _, row in compset_rates_df.iterrows():
                                check_in = datetime.datetime.strptime(row['checkIn'], '%Y-%m-%d').date()
                                check_out = datetime.datetime.strptime(row['checkOut'], '%Y-%m-%d').date()
                                
                                # Loop through each date in the range and create corresponding rows
                                compset_dates_expanded.extend([check_in + datetime.timedelta(days=i) for i in range((check_out - check_in).days)])

                            # Add dates column
                            compset_rates_df['dates'] = compset_dates_expanded

                            # Remove 'checkIn' and 'checkOut' columns
                            compset_rates_df = compset_rates_df.drop(columns=['checkIn', 'checkOut'])

                            # Reorder columns to make 'dates' the first column
                            compset_rates_df = compset_rates_df[['dates'] + [col for col in compset_rates_df.columns if col != 'dates']]

                            # Group by compsetHId
                            for compset_id, group in compset_rates_df.groupby("compsetHId"):
                                # Fetch the property name from verifiedproperties collection
                                compset_property = verifiedproperties.find_one({"hId": compset_id}, {"propertyName": 1})
                                compset_name = compset_property.get("propertyName", f"Unknown Property ({compset_id})")

                                # Dropdown filters for roomName and roomPlan in compset rates
                                compset_room_names = group['roomName'].unique()
                                compset_room_plans = group['roomPlan'].unique()

                                selected_compset_room_name = st.selectbox(
                                    f"Select Room Name for {compset_name}", compset_room_names, key=f"compset_room_name_{compset_id}"
                                )
                                selected_compset_room_plan = st.selectbox(
                                    f"Select Room Plan for {compset_name}", compset_room_plans, key=f"compset_room_plan_{compset_id}"
                                )

                                # Filter data based on selections
                                filtered_compset_rates = group[
                                    (group['roomName'] == selected_compset_room_name) &
                                    (group['roomPlan'] == selected_compset_room_plan)
                                ]

                                # Drop 'compsetHId' column from display
                                filtered_compset_rates = filtered_compset_rates.drop(columns=["compsetHId"])

                                # Display filtered table
                                st.subheader(f"Compset: {compset_name}")
                                st.dataframe(filtered_compset_rates)

    else:
        st.error("No active properties found in the database.")



