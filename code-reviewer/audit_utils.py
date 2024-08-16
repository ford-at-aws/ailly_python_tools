import logging

def read_file_content(file_path: str) -> str:
    """
    Read the content of a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: The content of the file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        logging.info(f"Read content from {file_path}")
        return content
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return ""

