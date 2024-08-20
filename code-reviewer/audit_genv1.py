import os
import logging
from typing import List
from audit_common import (
    create_temp_directory,
    write_files_to_process,
    read_files_to_process,
    remove_processed_file,
    load_template_content,
    copy_and_prepare_files,
    run_ailly_command,
    list_existing_temp_directories,
    list_python_files,
    list_ruby_files,
    process_file
)
from audit_utils import read_file_content as read_contents

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def prepare_standards_content(temp_dir: str) -> None:
    """Prepares necessary files in the temporary directory."""
    aillyrc_content = "You are an AWS software engineer"
    aillyrc_path = os.path.join(temp_dir, ".aillyrc")
    with open(aillyrc_path, "w") as f:
        f.write(aillyrc_content)
    logging.info(f"Created .aillyrc file with content: {aillyrc_content}")

    review_structure = load_template_content('template_v2.txt')
    review_path = os.path.join(temp_dir, "02_review_template.md")
    with open(review_path, "w") as f:
        f.write(review_structure)
    logging.info(f"Created 02_review_template file with content: {review_structure}")

    standards_content = load_template_content('standards.txt')
    standards_path = os.path.join(temp_dir, "01_standards.md")
    with open(standards_path, "w") as f:
        f.write(standards_content)
    logging.info(f"Created 01_standards.md file with content: {standards_content}")

def main() -> None:
    """Main function to start the auditing process."""
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
                    process_file(files[0], in_dir, temp_dir, out_dir, files_to_process_path, prepare_standards_content)
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
        process_file(all_files[0], in_dir, temp_dir, out_dir, files_to_process_path, prepare_standards_content)
        all_files = read_files_to_process(files_to_process_path)

if __name__ == "__main__":
    main()
