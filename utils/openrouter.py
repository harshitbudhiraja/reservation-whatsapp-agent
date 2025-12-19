import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def call_openrouter_llm(user_prompt, system_prompt, model, max_tokens=1000, temperature=0.9, top_p=0.9):

    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        print("OPENROUTER_API_KEY is not set")
        raise ValueError("OPENROUTER_API_KEY is not set")
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    )   


    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        
        if not completion.choices or not completion.choices[0].message.content:
            print("Response is empty or no choices returned")
            # print(f"Completion object: {completion.model_dump()}")
            with open('error_logs.json', 'a') as error_file:
                import json
                json.dump(completion.model_dump(), error_file, indent=2)
                error_file.write("\n")
            return ""
        
        return completion.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return ""
