import yaml
import os

# Hardcoded list of languages
languages_list = ["Python", "Ruby", "Java", "JavaScript", "C++", "Kotlin", ".NET", "Rust"]

def load_yaml(file_path):
    """Load the YAML content from the file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def get_snippet_tags(data, language):
    """Extract snippet tags for a specific language."""
    snippet_tags = []
    
    for section, content in data.items():
        if "languages" in content and language in content["languages"]:
            for version in content["languages"][language]["versions"]:
                for excerpt in version.get("excerpts", []):
                    snippet_tags.extend(excerpt.get("snippet_tags", []))
    
    return snippet_tags

def select_file_from_directory(directory):
    """List files in the directory and allow the user to select one."""
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.yaml')]
    
    if not files:
        print("No YAML files found in the directory.")
        return None
    
    print("Choose a file from the following list:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    
    choice = int(input("Enter the number of your choice: "))
    
    if choice < 1 or choice > len(files):
        print("Invalid choice. Exiting.")
        return None
    
    return os.path.join(directory, files[choice - 1])

def main():
    # Directory to search for files
    directory = "aws-doc-sdk-examples/.doc_gen/metadata"
    
    # Select a file
    file_path = select_file_from_directory(directory)
    if not file_path:
        return
    
    # Load the YAML file
    data = load_yaml(file_path)
    
    # Allow the user to select a language
    print("Choose a language from the following list:")
    for i, lang in enumerate(languages_list, 1):
        print(f"{i}. {lang}")
    
    choice = int(input("Enter the number of your choice: "))
    if choice < 1 or choice > len(languages_list):
        print("Invalid choice. Exiting.")
        return
    
    chosen_language = languages_list[choice - 1]
    
    # Get the snippet tags for the chosen language
    snippet_tags = get_snippet_tags(data, chosen_language)
    
    # Display the snippet tags
    if snippet_tags:
        print(f"\nSnippet tags for {chosen_language} in {file_path}:")
        for tag in snippet_tags:
            print(f"- {tag}")
    else:
        print(f"No snippet tags found for {chosen_language} in {file_path}.")

if __name__ == "__main__":
    main()
