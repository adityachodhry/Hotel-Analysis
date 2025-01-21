import streamlit as st
import pandas as pd
from pymongo import MongoClient
from chat import chatbot_response
from rate_display import display_rates
import requests
import datetime

# MongoDB connection
client = MongoClient("mongodb+srv://Retvens:JMdZt2hEPsqHuVQl@r-rate-shopper-cluster.nlstcxk.mongodb.net/")
db = client['ratex']
verifiedproperties = db['verifiedproperties']

def getAllProperties():
    query = {"isActive": True, "isRetvens": True}
    properties = list(verifiedproperties.find(query, {"hId": 1, "propertyName": 1, "_id": 0}))
    return properties

def fetch_rates(hId, start_date, end_date):
    api_url = "http://127.0.0.1:5000/get-rates"
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
st.set_page_config(page_title="Hotel Analysis", layout="wide")

# App Title
st.title("Hotel Analysis")

# Sidebar: Navigation
st.sidebar.header("Retvens Technologies")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Chat With Me"]
)

if page == "Home":
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
    st.header("Chat With Me")
    st.write("Ask me anything about the hospitality industry, and I'll provide insights!")

    search_query = st.sidebar.text_input("Search Property", "")

    properties = getAllProperties()
    if properties:
        property_options = [prop["propertyName"] for prop in properties]
        filtered_options = [opt for opt in property_options if search_query.lower() in opt.lower()]
        selected_property = st.sidebar.selectbox("Choose a Property", filtered_options)

        if selected_property:
            hId = next(prop['hId'] for prop in properties if prop['propertyName'] == selected_property)

            st.subheader(f"Selected Property: {selected_property}")

            user_input = st.text_input("Type your question here:", placeholder="e.g., Show rates for the next 10 days.")
            if user_input:
                response, extra = chatbot_response(user_input, selected_property=selected_property)
                st.subheader("Chatbot Response")
                st.write(response)

                if extra.get("fetch_rates"):
                    today = datetime.date.today()
                    if "next 10 days" in user_input.lower():
                        start_date = today.strftime('%Y-%m-%d')
                        end_date = (today + datetime.timedelta(days=10)).strftime('%Y-%m-%d')
                    elif "next 30 days" in user_input.lower():
                        start_date = today.strftime('%Y-%m-%d')
                        end_date = (today + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
                    else:
                        start_date = today.strftime('%Y-%m-%d')
                        end_date = (today + datetime.timedelta(days=10)).strftime('%Y-%m-%d')

                    rates = fetch_rates(hId, start_date, end_date)
                    if "error" in rates:
                        st.error(rates["error"])
                    else:
                        our_rates = rates.get("ourRates", [])
                        compset_rates = rates.get("compsetRates", [])

                        # Call the display_rates function
                        display_rates(our_rates, compset_rates, verifiedproperties)

    else:
        st.error("No active properties found in the database.")