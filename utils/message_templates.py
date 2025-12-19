MESSAGE_TEMPLATES = {
    "book_table": {
        "date": "What date would you like to book the table for?",
        "time": "What time would you like to book the table?",
        "restaurant_location": "Which location would you like to book at?\n\nWe have 20 centres, all across Delhi NCR.",
        "number_of_people": "How many people will be dining?"
    },
    "get_recommendation": {
        "user_lat": "To provide you with the best recommendations, please share your WhatsApp location.",
        "user_long": "To provide you with the best recommendations, please share your WhatsApp location."
    }
}

FUNCTION_REQUIRED_PARAMS = {
    "book_table": ["date", "time", "restaurant_location", "number_of_people"],
    "get_recommendation": ["user_lat", "user_long"]
}

def get_question_for_param(function_name, param_name):
    return MESSAGE_TEMPLATES.get(function_name, {}).get(param_name, f"Please provide {param_name}")

def get_missing_params_message(function_name, missing_params):
    if not missing_params:
        return None
    
    if len(missing_params) == 1:
        question = get_question_for_param(function_name, missing_params[0])
        return f"{question}"
    else:
        first_param = missing_params[0]
        question = get_question_for_param(function_name, first_param)
        return f"{question}"

