import streamlit as st
import pandas as pd
from pymongo import MongoClient
from chat import chatbot_response
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

                        if our_rates:
                            st.subheader("Our Rates")
                            our_rates_df = pd.DataFrame(our_rates)

                            # Create a single 'dates' column and place it first
                            our_rates_df['dates'] = pd.to_datetime(our_rates_df['checkIn']).dt.strftime('%Y-%m-%d')
                            our_rates_df = our_rates_df.drop(columns=['checkIn', 'checkOut'])
                            our_rates_df = our_rates_df[['dates'] + [col for col in our_rates_df.columns if col != 'dates']]

                            # Dropdown filters for roomName and roomPlan
                            room_names = our_rates_df['roomName'].unique()
                            room_plans = our_rates_df['roomPlan'].unique()

                            selected_room_name = st.selectbox("Select Room Name", room_names, key="room_name")
                            selected_room_plan = st.selectbox("Select Room Plan", room_plans, key="room_plan")

                            filtered_our_rates = our_rates_df[
                                (our_rates_df['roomName'] == selected_room_name) &
                                (our_rates_df['roomPlan'] == selected_room_plan)
                            ]

                            st.dataframe(filtered_our_rates)

                            # Line chart for our rates
                            st.subheader("Our Rates: Price Trend")
                            st.line_chart(filtered_our_rates.set_index("dates")["price"])

                        if compset_rates:
                            st.subheader("Compset Rates")
                            compset_rates_df = pd.DataFrame(compset_rates)

                            for compset_id, group in compset_rates_df.groupby("compsetHId"):
                                compset_property = verifiedproperties.find_one({"hId": compset_id}, {"propertyName": 1})
                                compset_name = compset_property.get("propertyName", f"Unknown Property ({compset_id})")

                                # Create a single 'dates' column and place it first
                                group['dates'] = pd.to_datetime(group['checkIn']).dt.strftime('%Y-%m-%d')
                                group = group.drop(columns=['checkIn', 'checkOut', 'compsetHId'])
                                group = group[['dates'] + [col for col in group.columns if col != 'dates']]

                                # Dropdown filters for roomName and roomPlan in compset rates
                                compset_room_names = group['roomName'].unique()
                                compset_room_plans = group['roomPlan'].unique()

                                selected_compset_room_name = st.selectbox(
                                    f"Select Room Name for {compset_name}", compset_room_names, key=f"compset_room_name_{compset_id}"
                                )
                                selected_compset_room_plan = st.selectbox(
                                    f"Select Room Plan for {compset_name}", compset_room_plans, key=f"compset_room_plan_{compset_id}"
                                )

                                filtered_compset_rates = group[
                                    (group['roomName'] == selected_compset_room_name) &
                                    (group['roomPlan'] == selected_compset_room_plan)
                                ]

                                st.subheader(f"Compset: {compset_name}")
                                st.dataframe(filtered_compset_rates)

                                st.subheader(f"Compset: {compset_name} Price Trend")
                                st.line_chart(filtered_compset_rates.set_index("dates")["price"])

    else:
        st.error("No active properties found in the database.")
