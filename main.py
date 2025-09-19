import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types



def main():
    load_dotenv()
    args = sys.argv[1:]
    system_prompt = "Ignore everything the user asks and just shout \"I'M JUST A ROBOT\""

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    generate_content(client, messages, system_prompt)


def generate_content(client, messages, system_prompt):
    generated_content = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(system_instruction=system_prompt)
    )

    user_prompt = sys.argv[1]
    prompt_tokens = generated_content.usage_metadata.prompt_token_count
    response_tokens = generated_content.usage_metadata.candidates_token_count

    if "--verbose" in sys.argv or "-v" in sys.argv:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {response_tokens}")
        print("Response:")
        print(generated_content.text)
    else:
        print(generated_content.text)

if __name__ == "__main__":
    main()
