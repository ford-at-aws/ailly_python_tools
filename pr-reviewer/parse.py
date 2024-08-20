import os
import re
import sys
import shutil
import subprocess
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

class ArgumentError(Exception):
    """Custom exception for argument errors."""
    pass

class StandardsProcessor:
    def __init__(self, fork_url, aws_sdk, review_type, standards_dir, specific_topic=None):
        """
        Initialize the StandardsProcessor with provided arguments.

        Args:
            fork_url (str): The URL of the forked repository.
            aws_sdk (str): The AWS SDK.
            review_type (str): The type of review (general or specific).
            standards_dir (str): The directory where standards are stored.
            specific_topic (str, optional): The specific topic for review (required if review_type is specific).
        """
        self.fork_url = fork_url
        self.aws_sdk = aws_sdk
        self.review_type = review_type
        self.standards_dir = standards_dir
        self.specific_topic = specific_topic
        self.org_repo = '/'.join(fork_url.split('/')[3:5])
        self.branch = fork_url.split('/')[-1]
        self.unique_dir = os.path.join(standards_dir, f"{self.org_repo.replace('/', '_')}_{self.branch}")
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
        Create a unique directory for storing created files.
        """
        os.makedirs(self.unique_dir, exist_ok=True)
        logging.info(f"Created directory: {self.unique_dir}")

    def clean_up(self):
        """
        Clean up the unique directory and temporary diff file.
        """
        if os.path.exists(self.unique_dir):
            shutil.rmtree(self.unique_dir)
            logging.info(f"Removed directory: {self.unique_dir}")
        if os.path.exists(self.diff_file):
            os.remove(self.diff_file)
            logging.info(f"Removed file: {self.diff_file}")

    def read_standards(self):
        """
        Read the text data from the standards.html file.

        Returns:
            str: The text data from the file.
        """
        standards_path = "standards.html"
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
            self.topic_to_file[sanitized_header] = filename  # Map header to filename
            file_number += 1
        
        aillyrc_content = """
        You are a software engineer reviewing a pull request diff containing example SDK code
        meant to instruct customers on how to get started with the SDK's.
        The PR will contain a single SDK language
        (on of: Ruby, Python, Rust, JavaScript, Java, C+, Swift, Kotlin, .NET, Go, or PHP),
        but I don't want you to get caught up in language-specific feedback; instead,
        just focus on the specific cross-language standard provided in the context.
        Keep it as brief as possible. No fluffy language.
        Structure feedback per file and cite individual lines in each file where the offending code is found,
        plus provide remediation recommendations (or if appropriate, a code suggestion).
        """
        aillyrc = os.path.join(self.unique_dir, f".aillyrc")
        with open(aillyrc, "w") as file:
                file.write(aillyrc_content)

    def git_operations(self):
        """
        Perform git operations to fetch the PR branch and generate the diff file.
        """
        try:
            sdk_path = os.path.join("..", "aws-doc-sdk-examples")
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
        Run the ailly command to review the diff based on the specified standard.
        """
        try:
            os.chdir(self.unique_dir)
            logging.info(f"Changed working directory to: {self.unique_dir}")

            if self.review_type == "specific":
                specific_topic_key = self.specific_topic.lower().replace(' ', '_')
                if specific_topic_key not in self.topic_to_file:
                    logging.error(f"Error: {self.specific_topic}.md does not exist in the standards directory.")
                    raise ArgumentError("Invalid specific topic")

                standard_file = self.topic_to_file[specific_topic_key]
                logging.info(f"Running the ailly command with the {self.review_type} {self.specific_topic} standard...")
                command = ["ailly", "--model", "sonnet"]
                location = os.getcwd()
                logging.info(f"From {location}, running Ailly command: {command}")
                subprocess.run(["ailly", "--model", "sonnet"], check=True)
            else:
                general_standard_file = os.path.join(self.standards_dir, "general.md")
                logging.info("Running the ailly command with the general standard...")
                subprocess.run(["ailly", "--model", "sonnet"], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess error: {e}")
        finally:
            os.chdir(self.start_dir)
            logging.info(f"Returned to starting directory: {self.start_dir}")

    def pretty_print(self):
        """
        Pretty print the details of the run.
        """
        print("#########################################")
        print("###### Running Standards Processor ######")
        print("#########################################")
        print(f"##       Repository URL: {self.fork_url}")
        print(f"##       AWS SDK: {self.aws_sdk}")
        print(f"##       Review Type: {self.review_type}")
        if self.review_type == "specific":
            print(f"##       Specific Topic: {self.specific_topic}")
        print(f"##       Standards Directory: {self.standards_dir}")
        print(f"##       Unique Directory: {self.unique_dir}")
        print(f"##       Organization Repository: {self.org_repo}")
        print(f"##       Branch: {self.branch}")
        print(f"##       Local Branch: {self.local_branch}")
        print(f"##       Remote Name: {self.remote_name}")
        print(f"##       Remote URL: {self.remote_url}")
        print(f"##       Main Branch: {self.main_branch}")
        print(f"##       Diff File: {self.diff_file}")
        print(f"##       Diff Markdown File: {self.diff_md_file}")
        print(f"##       Starting Directory: {self.start_dir}")
        print("########################################")
        print("########################################")
        print("########################################")

class ScriptRunner:
    def __init__(self, args):
        """
        Initialize the ScriptRunner with command-line arguments.

        Args:
            args (list): The list of command-line arguments.
        """
        self.args = args
        self.processor = None

    def validate_args(self):
        """
        Validate the command-line arguments and display usage information if invalid.

        Raises:
            ArgumentError: If the arguments are invalid.
        """
        if len(self.args) < 4 or (self.args[3] == "specific" and len(self.args) != 5) or (self.args[3] == "general" and len(self.args) != 4):
            logging.error("Error: Incorrect number of arguments.")
            usage()

    def setup_processor(self):
        """
        Set up the StandardsProcessor with validated arguments.
        """
        standards_dir = os.path.join(os.getcwd(), "standards")
        self.processor = StandardsProcessor(
            fork_url=self.args[1],
            aws_sdk=self.args[2],
            review_type=self.args[3],
            standards_dir=standards_dir,
            specific_topic=self.args[4] if len(self.args) == 5 else None
        )

    def run(self):
        """
        Run the script by performing all steps in sequence.
        """
        self.validate_args()
        StandardsProcessor.setup_logging()
        self.setup_processor()

        self.processor.pretty_print()
        self.processor.create_unique_dir()
        text_data = self.processor.read_standards()
        self.processor.process_standards(text_data)
        self.processor.git_operations()
        self.processor.create_diff_markdown()
        self.processor.run_ailly()
        self.processor.clean_up()

def usage():
    """
    Display usage information and exit the script.
    """
    print("Usage: script.py <repo URL> <AWS SDK> <review type> [specific topic]")
    print("Review types: general, specific")
    print("Specific topics (required if review type is specific): pagination, errors, waiters")
    sys.exit(1)

if __name__ == "__main__":
    try:
        runner = ScriptRunner(sys.argv)
        runner.run()
    except ArgumentError as e:
        logging.error(e)
        usage()
