import pandas as pd
import streamlit as st

def display_rates(our_rates, compset_rates, verifiedproperties):
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