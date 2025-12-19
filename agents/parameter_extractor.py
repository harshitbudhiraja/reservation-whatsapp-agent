import json
from utils.openrouter import call_openrouter_llm

def extract_parameters(user_input, function_name, missing_params, collected_params=None):

    system_prompt = f"""
    You are a parameter extraction agent. Your sole responsibility is to extract parameter values from user input.
    
    CURRENT FUNCTION: {function_name}
    MISSING PARAMETERS: {missing_params}
    ALREADY COLLECTED: {collected_params or {}}
    
    AVAILABLE FUNCTIONS AND THEIR PARAMETERS:
    1. book_table(date, meal_time, restaurant_location, number_of_people)
    2. get_recommendation(user_lat, user_long)
    
    RESPONSE FORMAT:
    Return ONLY a valid JSON object with no additional text:
    {{
    "arguments": {{
        "param1": "value1",
        "param2": "value2"
    }}
    }}
    
    RULES:
    - Extract ONLY the parameters that are mentioned in the user input
    - Focus on extracting values for the missing parameters: {missing_params}
    - If user provides a value for a parameter, include it in the arguments
    - If a parameter is not mentioned, do NOT include it (don't set to null)
    - Accept flexible formats (dates, times, numbers, locations)
    - For dates: accept "tomorrow", "today", "Dec 25", "25th December", etc.
    - For times: accept "7pm", "7:00 PM", "19:00", "evening", etc.
    - For numbers: extract numeric values from text
    - For locations: extract location names or descriptions
    
    EXAMPLES:
    Function: book_table, Missing: ["date", "time", "restaurant_location", "number_of_people"]
    Input: "tomorrow at 7pm"
    Output: {{"arguments": {{"date": "tomorrow", "time": "7pm"}}}}
    
    Function: book_table, Missing: ["date", "time", "restaurant_location", "number_of_people"]
    Input: "downtown for 4 people"
    Output: {{"arguments": {{"restaurant_location": "downtown", "number_of_people": "4"}}}}
    
    Function: get_recommendation, Missing: ["user_lat", "user_long"]
    Input: "I am in Connaught Place, can you recommend some nearby venues?"
    Output: {{"arguments": {{"user_lat": "28.6315", "user_long": "77.2167"}}}}
    
    Function: get_recommendation, Missing: ["user_long"]
    Input: "I am in Connaught Place, can you recommend some nearby venues?"
    Output: {{"arguments": {{"user_lat": "28.6315", "user_long": "77.2167"}}}}
    
    """

    user_prompt = f"User input: {user_input}\n\nExtract parameter values from the user input. Respond with JSON only:"

    llm_response = call_openrouter_llm(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        model="qwen/qwen3-8b",
        max_tokens=500,
        temperature=0.1,
        top_p=0.9
    )
    
    if llm_response:
        try:
            parsed_result = json.loads(llm_response)
            if isinstance(parsed_result, dict) and "arguments" in parsed_result:
                return json.dumps(parsed_result)
        except json.JSONDecodeError:
            start_idx = llm_response.find('{')
            if start_idx != -1:
                brace_count = 0
                end_idx = start_idx
                for i in range(start_idx, len(llm_response)):
                    if llm_response[i] == '{':
                        brace_count += 1
                    elif llm_response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                if end_idx > start_idx:
                    try:
                        json_str = llm_response[start_idx:end_idx]
                        parsed_result = json.loads(json_str)
                        if isinstance(parsed_result, dict) and "arguments" in parsed_result:
                            return json.dumps(parsed_result)
                    except json.JSONDecodeError:
                        pass
    
    result = {
        "arguments": {}
    }
    return json.dumps(result)

