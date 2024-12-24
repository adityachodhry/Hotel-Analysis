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
st.set_page_config(page_title="Hotel Price Prediction", layout="wide")

# App Title and Description
st.title("Hotel Price Prediction")
st.write("Select a property to analyze and predict future prices using AI.")

# Sidebar: Property Selection
st.sidebar.header("Select a Property")

# Fetch property list from MongoDB
properties = getAllProperties()

if properties:
    # Prepare dropdown options
    property_options = [prop["propertyName"] for prop in properties]
    
    # Search bar for filtering options
    search_query = st.sidebar.text_input("Search Property", "")
    
    # Filter dropdown based on search query
    filtered_options = [opt for opt in property_options if search_query.lower() in opt.lower()]
    
    # Dropdown for property selection
    selected_property = st.sidebar.selectbox("Choose a Property", filtered_options)
    
    if selected_property:
        st.subheader(f"Selected Property: {selected_property}")
        # Placeholder for additional functionality based on the selected property
        st.write("Additional analysis or prediction functionality can be implemented here.")
else:
    st.error("No active properties found in the database.")

