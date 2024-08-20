import os
import shutil
import logging
from datetime import datetime
import subprocess
from typing import List, Tuple


def create_temp_directory() -> Tuple[str, str, str]:
    """Creates a temporary directory with 'in' and 'out' subdirectories."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_dir = f"tmp_{timestamp}"
    in_dir = os.path.join(temp_dir, "in")
    out_dir = os.path.join(temp_dir, "out")
    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    logging.info(f"Created temporary directory: {temp_dir}")
    logging.info(f"Created 'in' subdirectory: {in_dir}")
    logging.info(f"Created 'out' subdirectory: {out_dir}")
    return temp_dir, in_dir, out_dir


def write_files_to_process(python_files: List[str], file_path: str) -> None:
    """Writes a list of Python files to the specified file."""
    with open(file_path, 'w') as f:
        for file in python_files:
            f.write(f"{file}\n")
    logging.info(f"Wrote {len(python_files)} files to {file_path}")


def read_files_to_process(file_path: str) -> List[str]:
    """Reads and returns a list of files to process from the specified file."""
    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r') as f:
        files = [line.strip() for line in f if line.strip()]
    logging.info(f"Loaded {len(files)} files from {file_path}")
    return files


def remove_processed_file(processed_file: str, file_path: str) -> None:
    """Removes a processed file from the list."""
    files = read_files_to_process(file_path)
    files = [file for file in files if file != processed_file]

    with open(file_path, 'w') as f:
        for file in files:
            f.write(f"{file}\n")

    logging.info(f"Removed processed file {processed_file} from {file_path}")


def load_template_content(template_name: str) -> str:
    """Loads the content of a template file from the 'templates' directory."""
    template_path = os.path.join('templates', template_name)
    if not os.path.exists(template_path):
        logging.error(f"Template {template_name} not found in 'templates' directory.")
        return ""
    with open(template_path, 'r') as file:
        return file.read()


def copy_and_prepare_files(file: str, in_dir: str, temp_dir: str, out_dir: str, prepare_content_func) -> None:
    """Copies the file to the input directory, prepares it, and processes it."""
    prepare_content_func(temp_dir)
    shutil.copy(file, in_dir)
    logging.info(f"Copied file {file} to {in_dir}")

    filename = os.path.basename(file)
    new_filename = f"04_{filename}.md"
    new_filepath = os.path.join(temp_dir, new_filename)

    original_content = read_contents(file)

    with open(new_filepath, 'w') as new_file:
        new_file.write(f"# File analyzed: {file}\n")
        new_file.write(original_content)

    logging.info(f"Renamed and moved file to {new_filepath}")

    run_ailly_command(temp_dir, out_dir, new_filename, file)

    if os.path.exists(new_filepath):
        os.remove(new_filepath)
        logging.info(f"Deleted file {new_filepath} after running 'ailly'")


def run_ailly_command(temp_dir: str, out_dir: str, file_name: str, original_filepath: str) -> None:
    """Runs the 'ailly' command on the specified file and handles the output."""
    try:
        command = f"ailly {file_name}"
        logging.info(f"Running command: {command} in directory: {temp_dir}")

        result = subprocess.run(command, cwd=temp_dir, capture_output=True, text=True, shell=True)
        logging.info(f"'ailly' command output:\n{result.stdout}")

        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.ailly.md'):
                    source_file = os.path.join(root, file)
                    renamed_file = os.path.join(out_dir,
                                                f"{os.path.splitext(os.path.basename(original_filepath))[0]}.md")
                    shutil.move(source_file, renamed_file)
                    logging.info(f"Moved and renamed '{file}' to '{renamed_file}'")

    except Exception as e:
        logging.error(f"Error running 'ailly': {e}")


def list_existing_temp_directories() -> List[str]:
    """Lists all existing temporary directories."""
    return [d for d in os.listdir() if os.path.isdir(d) and d.startswith("tmp_")]


def list_python_files(directory: str) -> List[str]:
    """Lists all Python files in the given directory."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != 'test_tools']
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                file_path = os.path.join(root, file)
                python_files.append(file_path)

    logging.info(f"Found {len(python_files)} Python files in {directory}")
    return python_files


def list_ruby_files(directory: str) -> List[str]:
    """Lists all Ruby files in the given directory."""
    ruby_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != 'test_tools']
        for file in files:
            if file.endswith('.rb') and not file.startswith('test_'):
                file_path = os.path.join(root, file)
                ruby_files.append(file_path)

    logging.info(f"Found {len(ruby_files)} Ruby files in {directory}")
    return ruby_files


def process_file(file: str, in_dir: str, temp_dir: str, out_dir: str, files_to_process_path: str,
                 prepare_content_func) -> None:
    """Processes a file by copying, preparing, and removing it."""
    logging.info(f"Processing file: {file}")
    copy_and_prepare_files(file, in_dir, temp_dir, out_dir, prepare_content_func)
    remove_processed_file(file, files_to_process_path)
