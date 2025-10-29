import os
from google.genai import types


schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Overwrites or creates new file with the given content depending on if the file already exists or not, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The location of the given file, relative to the working directory.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="The content you want to write to the file."
                ),
            },
        ),
    )

def write_file(working_directory, file_path, content):
    abs_working_dir = os.path.abspath(working_directory)
    file_dir = os.path.abspath(os.path.join(working_directory, file_path))

    if not file_dir.startswith(abs_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    try:
        if not os.path.exists(file_dir):
            os.makedirs(os.path.dirname(file_dir), exist_ok=True)
        
        if os.path.exists(file_dir) and os.path.isdir(file_dir):
            return f'Error: "{file_path}" is a directory, not a file'
        
        with open(file_dir, "w") as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f'Error writing to file: {e}'