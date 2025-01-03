def chatbot_response(user_input):
    """
    Function to handle chatbot interactions.
    Args:
        user_input (str): The question or statement from the user.

    Returns:
        str: The chatbot's response.
    """
    # Example Q&A database
    chatbot_responses = {
        "how can i increase hotel occupancy?": "Consider offering discounts, optimizing your online presence, and leveraging seasonal promotions to attract more guests.",
        "what is revenue per available room (revpar)?": "RevPAR stands for Revenue Per Available Room. It's calculated by multiplying your average daily rate (ADR) by your occupancy rate.",
        "how can i use dynamic pricing?": "Dynamic pricing involves adjusting your room rates based on demand, competition, and market trends. Tools like rate shoppers can help with this.",
        "how to improve guest satisfaction?": "Focus on personalized service, cleanliness, quick responses to issues, and actively collecting and acting on guest feedback."
    }

    # Find the response or provide a fallback
    return chatbot_responses.get(
        user_input.lower(), 
        "I'm not sure about that. Can you rephrase or ask another question?"
    )
