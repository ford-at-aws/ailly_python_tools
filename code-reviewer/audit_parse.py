import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple


def find_tmp_directories() -> List[str]:
    """
    Locate all directories with the prefix 'tmp_' in the current working directory and sort them by creation date.

    Returns:
        List[str]: A list of directory names starting with 'tmp_' sorted by creation date.
    """
    current_dir = os.getcwd()
    directories = [
        d for d in os.listdir(current_dir) if os.path.isdir(d) and d.startswith("tmp_")
    ]

    # Extract timestamps and sort directories
    directories_with_timestamps = []
    for directory in directories:
        timestamp_match = re.search(r"tmp_(\d+)", directory)
        if timestamp_match:
            timestamp = int(timestamp_match.group(1))
            directories_with_timestamps.append((directory, timestamp))

    # Sort directories by timestamp
    sorted_directories = sorted(directories_with_timestamps, key=lambda x: x[1])

    return [d[0] for d in sorted_directories]


def select_directory(directories: List[str]) -> str:
    """
    Prompt the user to select a directory from the provided list.

    Args:
        directories (List[str]): A list of directory names to choose from.

    Returns:
        str: The selected directory name.
    """
    print("Available directories:")
    for idx, directory in enumerate(directories):
        print(f"{idx + 1}: {directory}")
    selection = input("Select a directory by number: ")
    try:
        selected_index = int(selection) - 1
        if 0 <= selected_index < len(directories):
            return directories[selected_index]
        else:
            print("Invalid selection. Please try again.")
            return select_directory(directories)
    except ValueError:
        print("Invalid input. Please enter a number.")
        return select_directory(directories)


def remove_graymatter_headers(file_content: str) -> str:
    """
    Remove the GrayMatter header from the file content.

    Args:
        file_content (str): The content of the file as a string.

    Returns:
        str: The content of the file without the GrayMatter header.
    """
    # Regular expression to match GrayMatter headers
    header_pattern = re.compile(r"^---[\s\S]*?---\n")
    return re.sub(header_pattern, "", file_content, count=1)


def change_extension_to_py(file_path: str) -> str:
    """
    Change the file extension from .md to .py if applicable.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The new file path with .py extension if changed, otherwise the original file path.
    """
    base, ext = os.path.splitext(file_path)
    if ext == ".md":
        new_file_path = base + ".py"
        os.rename(file_path, new_file_path)
        return new_file_path
    return file_path


def load_and_validate_content(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load and validate the JSON content of the Python file.

    Args:
        file_path (str): The path to the file.

    Returns:
        Optional[Dict[str, Any]]: The parsed JSON content if valid, otherwise None.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            json_content = remove_graymatter_headers(content)
            data = json.loads(json_content)

            # Simple schema validation: checking for expected keys
            required_keys = {
                "resource",
                "pagination",
                "error_handling",
                "waiters",
                "threading",
            }
            if all(key in data for key in required_keys):
                return data
            else:
                print(f"Schema noncompliance in file: {file_path}")
                return None
    except Exception as e:
        print(f"Failed to load or validate {file_path}: {e}")
        return None


def process_directory(selected_dir: str) -> Tuple[List[str], List[str]]:
    """
    Process each file in the 'out' directory of the selected directory, removing headers and changing extensions.

    Args:
        selected_dir (str): The selected directory to process.

    Returns:
        Tuple[List[str], List[str]]: A tuple containing two lists:
            - The list of successfully processed files.
            - The list of files that failed to process.
    """
    out_dir = os.path.join(selected_dir, "out")
    success_list = []
    failed_list = []

    consolidated_dict = {
        "resource": [],
        "pagination": [],
        "error_handling": [],
        "waiters": [],
        "threading": [],
    }

    if not os.path.exists(out_dir) or not os.path.isdir(out_dir):
        print(f"No 'out' directory found in {selected_dir}.")
        return success_list, failed_list

    for filename in os.listdir(out_dir):
        file_path = os.path.join(out_dir, filename)

        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Remove the GrayMatter header
                new_content = remove_graymatter_headers(content)

                # Write the modified content back to the file
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(new_content)

                # Change the file extension to .py
                new_file_path = change_extension_to_py(file_path)
                success_list.append(os.path.basename(new_file_path))

                # Load and validate the content of the file
                data = load_and_validate_content(new_file_path)
                if data:
                    # Aggregate the data into the consolidated dictionary
                    consolidated_dict["resource"].extend(data.get("resource", []))
                    consolidated_dict["pagination"].extend(data.get("pagination", []))
                    consolidated_dict["error_handling"].extend(
                        data.get("error_handling", [])
                    )
                    consolidated_dict["waiters"].extend(data.get("waiters", []))
                    consolidated_dict["threading"].extend(data.get("threading", []))

            except Exception as e:
                print(f"Failed to process {filename}: {e}")
                failed_list.append(filename)

    # Save the consolidated dictionary to a new JSON file
    consolidated_file_path = os.path.join(out_dir, "consolidated_data.json")
    with open(consolidated_file_path, "w", encoding="utf-8") as consolidated_file:
        json.dump(consolidated_dict, consolidated_file, indent=4)

    print(f"\nConsolidated data saved to {consolidated_file_path}")

    # Generate a markdown report
    generate_markdown_report(consolidated_dict, out_dir)

    return success_list, failed_list


def generate_markdown_report(
    consolidated_dict: Dict[str, List[Dict[str, Any]]], output_dir: str
) -> None:
    """
    Generate a markdown report from the consolidated dictionary.

    Args:
        consolidated_dict (Dict[str, List[Dict[str, Any]]]): The consolidated data dictionary.
        output_dir (str): The directory to save the markdown report.
    """
    markdown_content = "# Consolidated Report\n\n"

    # Add summary table
    markdown_content += "## Summary Table\n\n"
    markdown_content += "| Category       | Count |\n"
    markdown_content += "|----------------|-------|\n"
    for key in consolidated_dict:
        markdown_content += f"| {key.capitalize()} | {len(consolidated_dict[key])} |\n"

    markdown_content += "\n"

    # Add detailed tables for each category
    for category in consolidated_dict:
        markdown_content += f"## {category.capitalize()} Table\n\n"
        if consolidated_dict[category]:
            markdown_content += "| File Name | Line Number | API Method | SDK Method | Recommendation |\n"
            markdown_content += "|-----------|-------------|------------|------------|----------------|\n"
            for item in consolidated_dict[category]:
                markdown_content += f"| {item['file_name']} | {item['line_number']} | {item['api_ref']} | {item['sdk_api_ref']} | {item['recommended']} |\n"
        else:
            markdown_content += "No items found in this category.\n"
        markdown_content += "\n"

    # Write to markdown file
    markdown_file_path = os.path.join(output_dir, "consolidated_report.md")
    with open(markdown_file_path, "w", encoding="utf-8") as markdown_file:
        markdown_file.write(markdown_content)

    print(f"Markdown report saved to {markdown_file_path}")


def main() -> None:
    """
    Main function to find and process directories, generating a consolidated report.
    """
    directories = find_tmp_directories()

    if not directories:
        print("No directories found with the prefix 'tmp_'.")
        return

    selected_dir = select_directory(directories)
    success_list, failed_list = process_directory(selected_dir)

    print("\nSuccessfully processed files:")
    for filename in success_list:
        print(f"- {filename}")

    if failed_list:
        print("\nFiles that failed to process:")
        for filename in failed_list:
            print(f"- {filename}")


if __name__ == "__main__":
    main()
