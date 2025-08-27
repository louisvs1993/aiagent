import os
from dotenv import load_dotenv
from google import genai
import sys



def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    if len(sys.argv) > 1:
        generated_content = client.models.generate_content(
            model="gemini-2.0-flash-001", 
            contents=sys.argv[1]
            )
        print("Prompt tokens:", generated_content.usage_metadata.prompt_token_count)
        print("Response tokens:", generated_content.usage_metadata.candidates_token_count)
        print("Response:")
        print(generated_content.text)
    else:
        raise Exception("No argument given")


if __name__ == "__main__":
    main()
