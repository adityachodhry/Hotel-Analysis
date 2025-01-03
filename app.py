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

def fetch_rates(hId):
    """
    Fetch rates for the next 10 days using the getRates API.
    Args:
        hId (int): Hotel ID for which rates are to be fetched.
    Returns:
        dict: Parsed JSON response from the API.
    """
    api_url = "http://127.0.0.1:5000/get-rates"  # Replace with deployed URL
    today = datetime.date.today()
    start_date = today.strftime('%Y-%m-%d')
    end_date = (today + datetime.timedelta(days=10)).strftime('%Y-%m-%d')
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
                    # Call fetch_rates to get rates
                    rates = fetch_rates(hId)
                    if "error" in rates:
                        st.error(rates["error"])
                    else:
                        # Separate our rates and compset rates
                        our_rates = rates.get("ourRates", [])
                        compset_rates = rates.get("compsetRates", [])

                        # Display our rates
                        if our_rates:
                            st.subheader("Our Rates")
                            our_rates_df = pd.DataFrame(our_rates)
                            st.dataframe(our_rates_df)

                        # Display compset rates grouped by compsetHId
                        if compset_rates:
                            st.subheader("Compset Rates")
                            compset_rates_df = pd.DataFrame(compset_rates)

                            # Group by compsetHId
                            for compset_id, group in compset_rates_df.groupby("compsetHId"):
                                # Fetch the property name from verifiedproperties collection
                                compset_property = verifiedproperties.find_one({"hId": compset_id}, {"propertyName": 1})
                                compset_name = compset_property.get("propertyName", f"Unknown Property ({compset_id})")

                                # Display table for each compset
                                st.subheader(f"Compset: {compset_name}")
                                st.dataframe(group.drop(columns=["compsetHId"]))  # Drop compsetHId from display

    else:
        st.error("No active properties found in the database.")
