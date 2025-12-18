import json
import re
from utils.openrouter import call_openrouter_llm

def classify_intent_and_extract_params(user_input):


    system_prompt = """
    You are an intent classification system that analyzes user input and maps it to the appropriate function.
    You should return the function name and arguments that best match the user's intent.
    AVAILABLE FUNCTIONS:
    1. book_table(date, time, restaurant_location, number_of_people)
    - Use when user wants to make a reservation or book a table
    
    2. get_table_status(table_id, restaurant_location)
    - Use when user wants to check status of a specific table or reservation
    
    3. get_menu_details()
    - Use when user asks about menu items, dishes, prices, or what's available

    RESPONSE FORMAT:
    Return ONLY a valid JSON object with no additional text:
    {
    "function": "function_name",
    "arguments": {
        "param1": "value1",
        "param2": "value2"
    }
    }

    RULES:
    - If no function matches, set "function": null and "arguments": {}
    - Extract all available parameters from user input, even if incomplete
    - For missing required parameters, set their value to null
    - Accept flexible date/time formats (convert to strings as-is)
    - Handle ambiguous queries by selecting the most likely function
    - Treat synonyms appropriately (e.g., "reserve" = book_table, "check reservation" = get_table_status)

    EXAMPLES:
    Input: "Book a table for 4 tomorrow at 7pm at downtown location"
    Output: {"function": "book_table", "arguments": {"date": "tomorrow", "time": "7pm", "restaurant_location": "downtown", "number_of_people": "4"}}

    Input: "What's the status of table 12?"
    Output: {"function": "get_table_status", "arguments": {"table_id": "12", "restaurant_location": null}}

    Input: "Show me your menu"
    Output: {"function": "get_menu_details", "arguments": {}}

    Input: "What's the weather like?"
    Output: {"function": null, "arguments": {}}
    """

    user_prompt = f"User input: {user_input}\n\nClassify the intent and extract parameters. Respond with JSON only:"

    llm_response = call_openrouter_llm(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        model="qwen/qwen3-8b",
        max_tokens=1000,
        temperature=0.1,
        top_p=0.9
    )
    print("llm_response", llm_response)
    if llm_response:
        print("llm_response", llm_response)

        try:
            parsed_result = json.loads(llm_response)

            if isinstance(parsed_result, dict) and "function" in parsed_result and "arguments" in parsed_result:
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
                        if isinstance(parsed_result, dict) and "function" in parsed_result and "arguments" in parsed_result:
                            return json.dumps(parsed_result)
                    except json.JSONDecodeError:
                        pass
    

    result = {
        "function": None,
        "arguments": {}
    }
    return json.dumps(result)


if __name__ == "__main__":
    user_input = "Make a reservation for 2 people on 18th December at 7:00 PM"
    print(classify_intent_and_extract_params(user_input))
