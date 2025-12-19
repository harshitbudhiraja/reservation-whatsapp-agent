from utils.openrouter import call_openrouter_llm

def time_to_hour_agent(time: str) -> int:
    """
    Uses LLM to extract the hour (0-23) from a given time string in various formats.
    Returns the hour as an integer (24-hour format).
    """

    system_prompt = """
        You are an expert at extracting the hour (0-23) in 24-hour format from a given time expression, regardless of the user's input format.
        Output ONLY a single integer (no extra text, no explanation, no quotes, no JSON).
        Examples:
        Input: "12:30 pm" → 12
        Input: "4pm" → 16
        Input: "2:05 AM" → 2
        Input: "18:45" → 18
        Input: "midnight" → 0
        Input: "noon" → 12
        Input: "11" → 11
        Input: "11 PM" → 23
        Input: "00:43" → 0
        Input: "7 o'clock in the evening" → 19
        Just reply with a single integer for the hour (0-23), nothing else.
    """
    user_prompt = f"""User time: {time}\n\nRespond ONLY with the hour (0-23) as per instructions."""
    llm_reply = call_openrouter_llm(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
        model="qwen/qwen3-8b",
        max_tokens=2000,
        temperature=0.01,
        top_p=0.95
    )
    try:
        hour_int = int(llm_reply.strip())
    except Exception as e:
        print("Error in time_to_hour_agent", str(e))
        hour_int = None
    return hour_int



if __name__ == "__main__":
    hour_int = time_to_hour_agent("12:30 pm")
    print(hour_int)