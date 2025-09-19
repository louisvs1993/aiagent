import os
from google.genai import types  


schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                ),
            },
        ),
    )

def get_files_info(working_directory, directory="."):
    abs_working_dir = os.path.abspath(working_directory)
    target_dir = os.path.abspath(os.path.join(working_directory, directory))
    
    if not target_dir.startswith(abs_working_dir):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    
    if not os.path.isdir(target_dir):
        f'Error: "{directory}" is not a directory'

    try:
        info=""
        for file in os.listdir(target_dir):
            file_path = os.path.join(target_dir, file)
            if not file.startswith("."):
                info = info + f"{file}: file_size={os.path.getsize(file_path)}, is_dir={os.path.isdir(file_path)}\n"
        return info
    except Exception as e:
        return f"Error listing files: {e}"
        