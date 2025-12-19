import json
import re
from utils.openrouter import call_openrouter_llm

def classify_intent(user_input):

    system_prompt = """
    You are an intent classification agent. Your sole responsibility is to identify which function the user wants to call.
    
    AVAILABLE FUNCTIONS:
    1. book_table(date, time, restaurant_location, number_of_people)
    - Use when user wants to make a reservation or book a table
    
    2. get_recommendation(user_lat, user_long)
    - Use when user wants to get recommendations for nearby venues

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
    - Focus ONLY on identifying the function the user wants
    - Extract any parameters that are explicitly mentioned in the user input
    - For parameters not mentioned, set their value to null
    - Accept flexible date/time formats (convert to strings as-is)
    - Handle ambiguous queries by selecting the most likely function
    - Be soft on the intent classification and don't be too strict.

    EXAMPLES:
    Input: "Book a table for 4 tomorrow at 7pm at downtown location"
    Output: {"function": "book_table", "arguments": {"date": "tomorrow", "time": "7pm", "restaurant_location": "downtown", "number_of_people": "4"}}

    Input: "I am in Connaught Place, can you recommend some nearby venues?"
    Output: {"function": "get_recommendation", "arguments": {"user_lat": "28.6315", "user_long": "77.2167"}}
    """
    
    user_prompt = f"User input: {user_input}\n\nClassify the intent and extract any explicitly mentioned parameters. Respond with JSON only:"

    llm_response = call_openrouter_llm(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        model="qwen/qwen3-8b",
        max_tokens=1000,
        temperature=0.1,
        top_p=0.9
    )

    if llm_response:

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
    user_input = "make a reservasation forads me , tomorrow at 4pm in Hauz khas, 4 people will be dining "
    print(classify_intent(user_input))
