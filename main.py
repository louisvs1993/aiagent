import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.write_file import schema_write_file
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file



def main():
    load_dotenv()
    args = sys.argv[1:]
    system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_write_file,
            schema_get_file_content,
            schema_run_python_file,
        ]
    )

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

    generate_content(client, messages, system_prompt, available_functions)


def generate_content(client, messages, system_prompt, available_functions):

    generated_content = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        )
    )

    user_prompt = sys.argv[1]
    prompt_tokens = generated_content.usage_metadata.prompt_token_count
    response_tokens = generated_content.usage_metadata.candidates_token_count

    if generated_content.function_calls:
        for function_call_part in generated_content.function_calls:
            print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
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
