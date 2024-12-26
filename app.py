import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient

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

# Streamlit page configuration
st.set_page_config(page_title="Hotel Analysis Tool", layout="wide")

# App Title
st.title("Hotel Analysis Tool")

# Sidebar: Navigation
# st.sidebar.image(
#     "retvensservices_logo.jpg", 
#     use_column_width=False, 
#     width=100  # Set your desired width in pixels
# )
st.sidebar.header("Retvens Technologies")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Revenue Forecasting", "Price Prediction"]
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
        Owners To Become Hotelier With solutions that make your life easy..
        """
    )

else:
    # Common Sidebar Content for Analysis Pages
    st.sidebar.header("Search Property")

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
            if page == "Revenue Forecasting":
                # Revenue Forecasting Page Content
                st.header("Revenue Forecasting")
                st.write("Select a property to analyze and forecast the revenue.")
                st.subheader(f"Selected Property: {selected_property}")
                st.write("You have selected: **Revenue Forecasting**")
                st.write("Additional analysis or forecasting functionality can be implemented here.")

            elif page == "Price Prediction":
                # Price Prediction Page Content
                st.header("Hotel Price Prediction")
                st.write("Select a property to analyze and predict future prices using AI.")
                st.subheader(f"Selected Property: {selected_property}")
                st.write("You have selected: **Price Prediction**")
                st.write("Additional analysis or prediction functionality can be implemented here.")
    else:
        st.error("No active properties found in the database.")
