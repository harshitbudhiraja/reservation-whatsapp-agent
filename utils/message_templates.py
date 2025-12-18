MESSAGE_TEMPLATES = {
    "book_table": {
        "date": "What date would you like to book the table for?",
        "time": "What time would you like to book the table?",
        "restaurant_location": "Which location would you like to book at?",
        "number_of_people": "How many people will be dining?"
    },
    "get_table_status": {
        "table_id": "Could you please provide your table ID?",
        "restaurant_location": "Which restaurant location should I check?"
    },
    "get_menu_details": {
        "restaurant_location": "Which location's menu would you like to see?"
    }
}

FUNCTION_REQUIRED_PARAMS = {
    "book_table": ["date", "time", "restaurant_location", "number_of_people"],
    "get_table_status": ["table_id", "restaurant_location"],
    "get_menu_details": ["restaurant_location"]
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

