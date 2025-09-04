import os

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