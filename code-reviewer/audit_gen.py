import os
import shutil
import logging
from datetime import datetime
import subprocess
from typing import List, Tuple

from audit_utils import read_file_content as read_contents 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_temp_directory() -> Tuple[str, str, str]:
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
    with open(file_path, 'w') as f:
        for file in python_files:
            f.write(f"{file}\n")
    logging.info(f"Wrote {len(python_files)} files to {file_path}")

def read_files_to_process(file_path: str) -> List[str]:
    if not os.path.exists(file_path):
        return []

    with open(file_path, 'r') as f:
        files = [line.strip() for line in f if line.strip()]
    logging.info(f"Loaded {len(files)} files from {file_path}")
    return files

def remove_processed_file(processed_file: str, file_path: str) -> None:
    files = read_files_to_process(file_path)
    files = [file for file in files if file != processed_file]

    with open(file_path, 'w') as f:
        for file in files:
            f.write(f"{file}\n")
    
    logging.info(f"Removed processed file {processed_file} from {file_path}")

def load_template_content(template_name: str) -> str:
    template_path = os.path.join('templates', template_name)
    if not os.path.exists(template_path):
        logging.error(f"Template {template_name} not found in 'templates' directory.")
        return ""
    with open(template_path, 'r') as file:
        return file.read()

def copy_and_prepare_files(file: str, in_dir: str, temp_dir: str, out_dir: str) -> None:
    aillyrc_content = "You are an AWS software engineer"
    aillyrc_path = os.path.join(temp_dir, ".aillyrc")
    with open(aillyrc_path, "w") as f:
        f.write(aillyrc_content)
    logging.info(f"Created .aillyrc file with content: {aillyrc_content}")

    # Load template content from files
    review_structure = load_template_content('template.txt')
    review_path = os.path.join(temp_dir, "02_review_template.md")
    with open(review_path, "w") as f:
        f.write(review_structure)

    standards_content = load_template_content('standards.txt')
    standards_path = os.path.join(temp_dir, "01_standards.md")
    with open(standards_path, "w") as f:
        f.write(standards_content)
    logging.info(f"Created 01_standards.md file with content: {standards_content}")

    shutil.copy(file, in_dir)
    logging.info(f"Copied file {file} to {in_dir}")

    filename = os.path.basename(file)
    new_filename = f"03_{filename}.md"
    new_filepath = os.path.join(temp_dir, new_filename)

    original_content = read_contents(file)

    with open(new_filepath, 'w') as new_file:
        new_file.write(f"# File analyzed: {file}\n")
        new_file.write(original_content)

    logging.info(f"Renamed and moved file to {new_filepath}")

    run_ailly_command(temp_dir, out_dir, new_filename, filename)

    if os.path.exists(new_filepath):
        os.remove(new_filepath)
        logging.info(f"Deleted file {new_filepath} after running 'ailly'")

def run_ailly_command(temp_dir: str, out_dir: str, file_name: str, original_filename: str) -> None:
    try:
        command = f"ailly {file_name}"
        logging.info(f"Running command: {command} in directory: {temp_dir}")

        result = subprocess.run(command, cwd=temp_dir, capture_output=True, text=True, shell=True)
        logging.info(f"'ailly' command output:\n{result.stdout}")

        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.ailly.md'):
                    source_file = os.path.join(root, file)
                    renamed_file = os.path.join(out_dir, f"{os.path.splitext(original_filename)[0]}.md")
                    shutil.move(source_file, renamed_file)
                    logging.info(f"Moved and renamed '{file}' to '{renamed_file}'")

    except Exception as e:
        logging.error(f"Error running 'ailly': {e}")

def list_existing_temp_directories() -> List[str]:
    return [d for d in os.listdir() if os.path.isdir(d) and d.startswith("tmp_")]

def list_python_files(directory: str) -> List[str]:
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
    ruby_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != 'test_tools']
        
        for file in files:
            if file.endswith('.rb') and not file.startswith('test_'):
                file_path = os.path.join(root, file)
                ruby_files.append(file_path)
    
    logging.info(f"Found {len(ruby_files)} Ruby files in {directory}")
    return ruby_files

def process_file(file: str, in_dir: str, temp_dir: str, out_dir: str, files_to_process_path: str) -> None:
    logging.info(f"Processing file: {file}")
    copy_and_prepare_files(file, in_dir, temp_dir, out_dir)
    remove_processed_file(file, files_to_process_path)

def main() -> None:
    choice = input("Do you want to analyze the Python or Ruby directories? (python/ruby): ").strip().lower()

    if choice == 'python':
        base_directory = "aws-doc-sdk-examples/python/example_code"
    elif choice == 'ruby':
        base_directory = "aws-doc-sdk-examples/ruby/example_code"
    else:
        print("Invalid choice. Exiting.")
        return

    subdirectories = [d for d in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, d))]
    subdirectories.append('All')

    print("\nAvailable subdirectories in example_code:")
    for idx, subdir in enumerate(subdirectories, start=1):
        print(f"{idx}. {subdir}")

    subdirectory_choice = input("Select a subdirectory or 'All' to process (enter the number): ").strip()

    try:
        subdirectory_choice = int(subdirectory_choice)
        if subdirectory_choice < 1 or subdirectory_choice > len(subdirectories):
            raise ValueError("Choice out of range.")
    except ValueError:
        print("Invalid choice. Exiting.")
        return

    selected_subdirectory = subdirectories[subdirectory_choice - 1]

    if selected_subdirectory == 'All':
        directories_to_process = [os.path.join(base_directory, subdir) for subdir in subdirectories if subdir != 'All']
    else:
        directories_to_process = [os.path.join(base_directory, selected_subdirectory)]

    existing_temp_dirs = list_existing_temp_directories()

    for temp_dir in existing_temp_dirs:
        files_to_process_path = os.path.join(temp_dir, "files_to_process.txt")
        if os.path.exists(files_to_process_path):
            files = read_files_to_process(files_to_process_path)
            if files:
                input(f"Press enter to continue processing from {temp_dir}. {len(files)} files left.")
                in_dir = os.path.join(temp_dir, "in")
                out_dir = os.path.join(temp_dir, "out")
                while files:
                    process_file(files[0], in_dir, temp_dir, out_dir, files_to_process_path)
                    files = read_files_to_process(files_to_process_path)
                return

    temp_dir, in_dir, out_dir = create_temp_directory()

    all_files = []
    for directory in directories_to_process:
        if choice == 'python':
            all_files.extend(list_python_files(directory))
        elif choice == 'ruby':
            all_files.extend(list_ruby_files(directory))

    files_to_process_path = os.path.join(temp_dir, "files_to_process.txt")
    write_files_to_process(all_files, files_to_process_path)

    input(f"Press enter to start processing. {len(all_files)} files to process.")

    while all_files:
        process_file(all_files[0], in_dir, temp_dir, out_dir, files_to_process_path)
        all_files = read_files_to_process(files_to_process_path)

if __name__ == "__main__":
    main()
