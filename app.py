import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Set Streamlit page configuration
st.set_page_config(page_title="Hotel Price Prediction", layout="wide")

# App Title and Description
st.title("Hotel Price Prediction")
st.write("Upload your hotel data to predict future price using AI.")

# Sidebar: File Upload
st.sidebar.header("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.subheader("Uploaded Data Preview")
    st.write(data.head())

    # Sidebar: Feature Selection
    st.sidebar.subheader("Model Configuration")
    target_feature = st.sidebar.selectbox("Select Target Feature", data.columns)
    feature_columns = st.sidebar.multiselect("Select Features for Prediction", data.columns)

    if st.sidebar.button("Train Model"):
        if target_feature and feature_columns:
            X = data[feature_columns]
            y = data[target_feature]

            # Data Split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Model Training
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)

            # Predictions
            predictions = model.predict(X_test)
            mse = mean_squared_error(y_test, predictions)

            # Display Results
            st.subheader("Model Performance")
            st.write(f"Mean Squared Error: {mse:.2f}")

            st.subheader("Prediction Results")
            results = pd.DataFrame({"Actual": y_test, "Predicted": predictions})
            st.write(results.head())

        else:
            st.error("Please select a target and features for prediction.")
else:
    st.info("Upload a CSV file to start.")