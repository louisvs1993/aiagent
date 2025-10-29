import os
from config import MAX_CHARS
from google.genai import types


schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Returns the content of a given file, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The location of the given file, relative to the working directory.",
                ),
            },
        ),
    )


def get_file_content(working_directory, file_path):
    abs_working_dir = os.path.abspath(working_directory)
    file_dir = os.path.abspath(os.path.join(working_directory, file_path))

    if not file_dir.startswith(abs_working_dir):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(file_dir):
        f'Error: File not found or is not a regular file: "{file_path}"'
    
    try:
        with open(file_dir, "r") as f:
            file_content_string = ""
            if len(f.read()) > MAX_CHARS:
                f.seek(0)
                file_content_string = f.read(MAX_CHARS)
                file_content_string = f"{file_content_string}[...File {file_path} truncated at 10000 characters]"
            else:
                f.seek(0)
                file_content_string = f.read(MAX_CHARS)
            return file_content_string
    except Exception as e:
        return f'Error reading file "{file_path}": {e}'
