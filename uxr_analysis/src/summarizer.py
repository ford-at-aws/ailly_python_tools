import logging
import os
import shutil
import subprocess

from .config_manager import ConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Summarizer:
    def __init__(self, output_dir: str):
        """
        Initialize the Summarizer with the specified output directory.

        :param output_dir: The directory where all output files will be stored.
        """
        self.output_dir = output_dir
        self.config_file = os.path.join(output_dir, "uxr_config.json")
        self.transcripts_dir = os.path.join(output_dir, "parsed_transcriptions")
        self.ensure_directory(self.transcripts_dir)
        self.user_testing_review_dir = os.path.join(self.output_dir, "user_testing_review")
        self.results_dir = os.path.join(self.output_dir, "results")
        self.config_data = ConfigManager.load_config(self.output_dir)
        self.template_file = self.config_data["methodology"]
        self.aillyrc_file = self.config_data["aillyrc"]

    def ensure_directory(self, directory: str) -> None:
        """
        Ensure the specified directory exists. Raise an error if the directory is invalid.

        :param directory: The directory path to check.
        :raises FileNotFoundError: If the directory does not exist.
        """
        if not os.path.isdir(directory):
            logger.error(f"Error: '{directory}' is not a valid directory.")
            raise FileNotFoundError(f"Directory '{directory}' does not exist.")

    def create_directory(self, directory: str) -> None:
        """
        Create the specified directory if it does not already exist.

        :param directory: The directory path to create.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Creating project directory: {directory}")

    def create_file(self, file_path: str, content: str) -> None:
        """
        Create a file with the specified content.

        :param file_path: The path of the file to create.
        :param content: The content to write to the file.
        """
        with open(file_path, "w") as file:
            file.write(content)
        logger.info(f"Created file: {file_path}")

    def summarize_transcripts(self) -> None:
        """
        Summarize transcripts by generating markdown files and running an AI-based model.

        This method reads transcripts from the `parsed_transcriptions` directory,
        creates relevant markdown files for processing, runs the AI model using `npx ailly`,
        and then moves the results to the `results` directory.
        """
        self.create_directory(self.user_testing_review_dir)
        self.create_directory(self.results_dir)

        # Read the template content from the file
        with open(self.template_file, "r") as file:
            template_content = file.read()

        # Read the aillyrc content from the file
        with open(self.aillyrc_file, "r") as file:
            aillyrc_content = file.read()

        # Write the aillyrc content to the .aillyrc file
        self.create_file(
            os.path.join(self.user_testing_review_dir, ".aillyrc"), aillyrc_content
        )

        # Write the template content to the file
        self.create_file(
            os.path.join(self.user_testing_review_dir, "10_template.md"),
            template_content,
        )

        for transcript_file in os.listdir(self.transcripts_dir):
            if transcript_file.endswith(".json"):
                transcript_path = os.path.join(self.transcripts_dir, transcript_file)
                transcript_basename = os.path.splitext(transcript_file)[0]
                logger.info(f"Processing transcript file: {transcript_path}")

                with open(transcript_path, "r") as file:
                    transcript_text = file.read()

                self.create_file(
                    os.path.join(
                        self.user_testing_review_dir, f"20_{transcript_basename}.md"
                    ),
                    f"---\nprompt: >\n  {transcript_text}\n---",
                )
                self.create_file(
                    os.path.join(
                        self.user_testing_review_dir,
                        f"30_analysis_{transcript_basename}.md",
                    ),
                    "---\nprompt: >\n  Using the template and transcript provided, fill out the table with participant comments for each step. Add an extra column and add a summary of the commentary for each step.\n---",
                )

                current_dir = os.getcwd()
                os.chdir(self.user_testing_review_dir)
                logger.info(f"⚙️ Running Ailly for transcript: {transcript_basename}")
                subprocess.run(["npx", "ailly"])

                output_file = f"30_analysis_{transcript_basename}.md.ailly.md"
                shutil.move(
                    output_file,
                    os.path.join(
                        "..", "..", self.results_dir, f"{transcript_basename}.md"
                    ),
                )
                logger.info(
                    f"Copied output file to results directory: {os.path.join('..', self.results_dir, f'{transcript_basename}.md')}"
                )

                # Clean up temporary files
                for temp_file in os.listdir("."):
                    if temp_file.startswith("20_") or temp_file.startswith("30_"):
                        os.remove(temp_file)

                os.chdir(current_dir)
        logger.info(f"Analysis completed ✅ See: {self.output_dir}/results")
        shutil.rmtree(self.user_testing_review_dir)
