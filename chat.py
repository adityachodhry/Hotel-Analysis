import requests

def chatbot_response(user_input, selected_property=None):
    """
    Function to handle chatbot interactions.
    Args:
        user_input (str): The question or statement from the user.
        selected_property (str, optional): Selected property name for rate queries.
    Returns:
        tuple: (str: response message, dict: additional data)
    """
    chatbot_responses = {
        "how can i increase hotel occupancy?": "To increase hotel occupancy, focus on a combination of strategic initiatives designed to attract more guests and enhance their overall experience. Start by offering competitive discounts or exclusive deals, such as early booking discounts, last-minute offers, or packages that include additional services like meals or spa treatments. Ensure your online presence is optimized by maintaining a user-friendly website, being active on social media, and listing your property on popular booking platforms with high-quality photos and positive reviews to build trust with potential guests. Seasonal promotions, such as special packages for holidays or local events, can also draw in travelers looking for unique experiences. Partner with travel agencies, local tour operators, and corporate organizations to secure bulk bookings or repeat business. Lastly, prioritize personalized guest experiences by tailoring services to their preferences, offering loyalty programs, and consistently delivering exceptional customer service. By implementing these strategies, you can effectively boost occupancy rates while enhancing guest satisfaction and loyalty.",
        "what is revenue per available room (revpar)?": "RevPAR stands for Revenue Per Available Room. It's calculated by multiplying your average daily rate (ADR) by your occupancy rate.",
        "how can i use dynamic pricing?": "Dynamic pricing involves adjusting your room rates based on demand, competition, and market trends. Tools like rate shoppers can help with this.",
        "how to improve guest satisfaction?": "Focus on personalized service, cleanliness, quick responses to issues, and actively collecting and acting on guest feedback.",
    }

    # Check for rate-related query
    if "rates" in user_input.lower() and selected_property:
        return ("Fetching rates for the next 10 days...", {"fetch_rates": True})

    # Default chatbot response
    return (chatbot_responses.get(user_input.lower(), "I'm not sure about that. Can you rephrase or ask another question?"), {})
