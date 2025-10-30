import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.write_file import schema_write_file
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from call_function import call_function



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

If a tool can accomplish the request, respond with a function call. Prefer defaults when obvious (e.g., run tests.py with no extra args). Do not ask for arguments unless strictly necessary.
"""

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_write_file,
            schema_get_file_content,
            schema_run_python_file,
        ]
    )

    verbose = False

    if "--verbose" in args:
        verbose = True
        args.remove("--verbose")

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

    for i in range(20):
        done = generate_content(client, messages, system_prompt, available_functions, verbose=verbose)
        if done:
            break


def generate_content(client, messages, system_prompt, available_functions, verbose=False):
    try:
        generated_content = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            )
        )

        for cand in generated_content.candidates:
            messages.append(cand.content)

        user_prompt = sys.argv[1]
        prompt_tokens = generated_content.usage_metadata.prompt_token_count
        response_tokens = generated_content.usage_metadata.candidates_token_count

        if generated_content.function_calls:
            for function_call_part in generated_content.function_calls:
                print(f"- Calling function: {function_call_part.name}")
                function_call_result = call_function(function_call_part, verbose=verbose)

                # validate structure
               
                tool_response = function_call_result.parts[0].function_response.response
                tool_name = function_call_part.name
                messages.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response=tool_response,
                                )
                            )
                        ],
                    )
                )
                if verbose:
                    print(f"-> {tool_response}")
            return False

        else:
            # simple fallback for obvious requests
            lower = user_prompt.lower()
            if "run tests.py" in lower or ("run" in lower and "tests.py" in lower):
                fc = types.FunctionCall(
                    name="run_python_file",
                    args={"file_path": "tests.py"},
                )
                print(f"- Calling function: {fc.name}")
                function_call_result = call_function(fc, verbose=verbose)
                tool_response = function_call_result.parts[0].function_response.response

                tool_name = fc.name
                messages.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response=tool_response,
                                )
                            )
                        ],
                    )
                )

                if verbose:
                    print(f"-> {tool_response}")

            if verbose:
                print(f"User prompt: {user_prompt}")
                print(f"Prompt tokens: {prompt_tokens}")
                print(f"Response tokens: {response_tokens}")
                print("Response:")

        if generated_content.text:
            print(generated_content.text)
            return True

        return False
    except Exception as e:
        print(e)
        return True
    

if __name__ == "__main__":
    main()
