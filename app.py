import streamlit as st
import pandas as pd
import numpy as np
from pymongo import MongoClient
from chat import chatbot_response  

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
            # Display selected property
            st.subheader(f"Selected Property: {selected_property}")

            # Chatbot interaction
            st.write("Ask a question about the hospitality industry:")

            # User input for chatbot
            user_input = st.text_input("Type your question here:", placeholder="e.g., How can I increase hotel occupancy?")

            # Generate chatbot response
            if user_input:
                response = chatbot_response(user_input)
                st.subheader("Chatbot Response")
                st.write(response)

    else:
        st.error("No active properties found in the database.")
