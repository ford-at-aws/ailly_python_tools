import glob
import os
import re
import shutil
import subprocess
import sys
import logging

def convert_to_gray_matter_header(content):
    """
    Converts the given content into an indented gray matter header format.
    """
    header_content = """---
prompt: |
    {}
combined: true
---""".format(content.replace('\n', '\n    '))
    return header_content

class StandardsProcessor:
    def __init__(self, fork_url):
        """
        Initialize the StandardsProcessor with the provided fork URL.

        Args:
            fork_url (str): The URL of the forked repository.
        """
        self.fork_url = fork_url
        self.org_repo = '/'.join(fork_url.split('/')[3:5])
        self.branch = fork_url.split('/')[-1]
        self.standards_dir = os.path.join(os.getcwd(), "standards")
        self.unique_dir = os.path.join(self.standards_dir, f"{self.org_repo.replace('/', '_')}_{self.branch}")
        self.start_dir = os.getcwd()
        self.top_level_standards_file = os.path.join(self.start_dir, "templates", "standards.html")
        self.local_branch = f"pr-{self.branch}"
        self.remote_name = "temp_remote"
        self.remote_url = f"https://github.com/{self.org_repo}.git"
        self.main_branch = "main"
        self.diff_file = os.path.join(self.standards_dir, "pr_diff.txt")
        self.diff_md_file = os.path.join(self.standards_dir, "09_pr_diff.md")
        self.start_dir = os.getcwd()
        self.topic_to_file = {}  # Dictionary to map topics to filenames

    @staticmethod
    def setup_logging():
        """
        Set up logging configuration.
        """
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitize the filename by replacing invalid characters with underscores.

        Args:
            filename (str): The filename to sanitize.

        Returns:
            str: The sanitized filename.
        """
        return re.sub(r"[^\w\-_\. ]", "_", filename)

    def create_unique_dir(self):
        """
        Create a unique directory for storing created files and copy the standards.html file.
        """
        os.makedirs(self.unique_dir, exist_ok=True)
        logging.info(f"Created unique directory: {self.unique_dir}")

        # Copy standards.html to the unique directory
        destination_path = os.path.join(self.unique_dir, "standards.html")
        if not os.path.exists(destination_path):
            shutil.copy(self.top_level_standards_file, destination_path)
            logging.info(f"Copied standards.html to: {destination_path}")

    def read_standards(self):
        """
        Read the text data from the standards.html file.

        Returns:
            str: The text data from the file.
        """
        standards_path = os.path.join(self.unique_dir, "standards.html")
        with open(standards_path, "r") as file:
            return file.read()

    def process_standards(self, text_data):
        """
        Process the standards from the text data and create markdown files.

        Args:
            text_data (str): The text data containing the standards.
        """
        sections = text_data.split("<details>")[1:]
        file_number = 10

        for section in sections:
            header = section.split("<summary><h2>")[1].split("</h2></summary>")[0]
            content = section.split("</summary>")[1].strip()
            sanitized_header = self.sanitize_filename(header.lower().replace(' ', '_'))
            filename = os.path.join(self.unique_dir, f"{file_number}_{sanitized_header}.md")

            gray_matter_content = convert_to_gray_matter_header(content.strip("</details>"))

            with open(filename, "w") as file:
                file.write(gray_matter_content)

            logging.info(f"Created file: {filename}")
            file_number += 1

        aillyrc_content = """
        You are a software engineer reviewing a pull request diff containing example SDK code
        meant to instruct customers on how to get started with the SDK's.
        The PR will contain a single SDK language
        (one of: Ruby, Python, Rust, JavaScript, Java, C+, Swift, Kotlin, .NET, Go, or PHP),
        but I don't want you to get caught up in language-specific feedback; instead,
        just focus on the specific language-agnostic standard provided in the context.
        Keep it as brief as possible. No fluffy language.
        Present feedback in a markdown table, with columns for filename, line number, severity (low/medium/high/critical), issue description, and recommendation,
        sorted by severity:
        E.g. 
        | Filename | Line Number | Severity | Issue Description | Recommendation |
        | --- | --- | --- | --- | --- |
        | S3BatchScenario.java | 154 | High | The catch block for S3Exception and RuntimeException is too broad, potentially hiding important information about the root cause of the error. | Consider separating the catch blocks or providing more specific error handling and logging for different exception types. |
        | S3BatchActions.java | 166, 260, 269, 279, 323, 334, 346, 389, 411, 425, 435 | High | The code is catching a broad RuntimeException, which can potentially hide the root cause of errors and make it harder to debug. | Consider catching more specific exception types or providing better error handling and logging to make it easier to diagnose and fix issues. |
        """
        aillyrc = os.path.join(self.unique_dir, f".aillyrc")
        with open(aillyrc, "w") as file:
            file.write(aillyrc_content)
    
    def git_operations(self):
        """
        Perform git operations to fetch the PR branch and generate the diff file.
        """
        try:
            sdk_path = os.path.join("..", "..", "aws-doc-sdk-examples")
            if not os.path.isdir(sdk_path):
                logging.error("Error: Unable to navigate to the specified AWS SDK directory.")
                raise ArgumentError("Invalid AWS SDK directory")

            os.chdir(sdk_path)
            logging.info(f"Navigated to: {sdk_path}")

            subprocess.run(["git", "remote", "add", self.remote_name, self.remote_url], check=True)
            subprocess.run(["git", "fetch", self.remote_name, f"{self.branch}:{self.local_branch}"], check=True)
            subprocess.run(["git", "checkout", self.main_branch], check=True)
            subprocess.run(["git", "pull", "origin", self.main_branch], check=True)
            logging.info(f"Fetched and checked out branch: {self.branch}")

            with open(self.diff_file, "w") as diff_file:
                subprocess.run(["git", "diff", f"{self.main_branch}...{self.local_branch}"], stdout=diff_file, check=True)
            logging.info(f"Generated diff and saved to: {self.diff_file}")

            subprocess.run(["git", "branch", "-D", self.local_branch], check=True)
            subprocess.run(["git", "remote", "remove", self.remote_name], check=True)
            logging.info(f"Cleaned up local branches and remote: {self.remote_name}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess error: {e}")
            self.clean_up()
            sys.exit(1)
        finally:
            os.chdir(self.start_dir)
            logging.info(f"Returned to starting directory: {self.start_dir}")

    def create_diff_markdown(self):
        """
        Create a markdown file from the generated diff file with a greymatter head.
        """
        diff_md_filename = os.path.basename(self.diff_md_file)
        unique_diff_md_file = os.path.join(self.unique_dir, diff_md_filename)

        with open(unique_diff_md_file, 'w') as md_file:
            md_file.write("---\nprompt: This is a git diff describing the change and that I would like for a software engineer to review for standards.\nskip: true\n---\n")
            with open(self.diff_file, 'r') as diff_file:
                md_file.write(diff_file.read())
        
        logging.info(f"Created markdown file with greymatter head: {self.diff_md_file}")

    def run_ailly(self):
        """
        Run the Ailly command to review the diff based on the specified standard.
        """
        try:
            os.chdir(self.unique_dir)
            logging.info(f"Changed working directory to: {self.unique_dir}")
            subprocess.run(["ailly", "--model", "sonnet", "--verbose"], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess error: {e}")
        finally:
            os.chdir(self.start_dir)
            logging.info(f"Returned to starting directory: {self.start_dir}")

    def rename_files(self):
        """
        Rename the processed Ailly files to shorter forms.
        """
        for file in os.listdir(self.unique_dir):
            if file.endswith(".ailly.md"):
                new_name = re.sub(r'^\d+_', '', file).replace('.ailly.md', '')
                old_path = os.path.join(self.unique_dir, file)
                new_path = os.path.join(self.unique_dir, new_name)
                os.rename(old_path, new_path)
                logging.info(f"Renamed file {old_path} to {new_path}")

        # Define a pattern to match files with a numeric prefix
        pattern = os.path.join(self.unique_dir, '[0-9]*')
        files_to_delete = glob.glob(pattern)
        for file in files_to_delete:
            if re.match(r'^\d', os.path.basename(file)):
                os.remove(file)
                print(f'Deleted: {file}')


    def run(self):
        """
        Run the StandardsProcessor.
        """
        self.setup_logging()
        self.create_unique_dir()
        text_data = self.read_standards()
        self.process_standards(text_data)
        self.git_operations()
        self.create_diff_markdown()
        self.run_ailly()
        self.rename_files()
        logging.info("Processing complete.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python review.py <fork URL>")
        sys.exit(1)

    fork_url = sys.argv[1]
    processor = StandardsProcessor(fork_url=fork_url)
    processor.run()
