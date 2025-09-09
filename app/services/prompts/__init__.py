import os

def read_prompt(filename="data.txt"):
    # Get the current folder path dynamically
    file_path = os.path.join(os.path.dirname(__file__), filename)

    # Read the content
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()