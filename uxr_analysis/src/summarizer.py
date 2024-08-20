import os
import shutil
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.transcripts_dir = os.path.join(output_dir, 'parsed_transcriptions')
        self.ensure_directory(self.transcripts_dir)
        self.user_testing_review_dir = os.path.join(self.output_dir, 'user_testing_review')
        self.results_dir = os.path.join(self.output_dir, 'results')
        self.template_file = os.path.join("templates", "methodology.txt")
        self.aillyrc_file = os.path.join("templates", "aillyrc.txt")

    def ensure_directory(self, directory):
        if not os.path.isdir(directory):
            logger.error(f"Error: '{directory}' is not a valid directory.")
            raise FileNotFoundError(f"Directory '{directory}' does not exist.")

    def create_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Creating project directory: {directory}")

    def create_file(self, file_path, content):
        with open(file_path, 'w') as file:
            file.write(content)
        logger.info(f"Created file: {file_path}")

    def summarize_transcripts(self):
        self.create_directory(self.user_testing_review_dir)
        self.create_directory(self.results_dir)

        # Read the template content from the file
        with open(self.template_file, 'r') as file:
            template_content = file.read()

        # Read the aillyrc content from the file
        with open(self.aillyrc_file, 'r') as file:
            aillyrc_content = file.read()

        # Write the aillyrc content to the .aillyrc file
        self.create_file(os.path.join(self.user_testing_review_dir, '.aillyrc'), aillyrc_content)

        # Write the template content to the file
        self.create_file(os.path.join(self.user_testing_review_dir, '10_template.md'), template_content)

        for transcript_file in os.listdir(self.transcripts_dir):
            if transcript_file.endswith('.json'):
                transcript_path = os.path.join(self.transcripts_dir, transcript_file)
                transcript_basename = os.path.splitext(transcript_file)[0]
                logger.info(f"Processing transcript file: {transcript_path}")

                with open(transcript_path, 'r') as file:
                    transcript_text = file.read()

                self.create_file(os.path.join(self.user_testing_review_dir, f"20_{transcript_basename}.md"), f"---\nprompt: >\n  {transcript_text}\n---")
                self.create_file(os.path.join(self.user_testing_review_dir, f"30_analysis_{transcript_basename}.md"),
                                "---\nprompt: >\n  Using the template and transcript provided, fill out the table with participant comments for each step. Add an extra column and add a summary of the commentary for each step.\n---")

                current_dir = os.getcwd()
                os.chdir(self.user_testing_review_dir)
                logger.info(f"⚙️ Running Ailly for transcript: {transcript_basename}")
                subprocess.run(["npx", "ailly"])

                output_file = f"30_analysis_{transcript_basename}.md.ailly.md"
                shutil.move(output_file, os.path.join('..', '..', self.results_dir, f"{transcript_basename}.md"))
                logger.info(f"Copied output file to results directory: {os.path.join('..', self.results_dir, f'{transcript_basename}.md')}")

                for temp_file in os.listdir('.'):
                    if temp_file.startswith('20_') or temp_file.startswith('30_'):
                        os.remove(temp_file)

                os.chdir(current_dir)
        logger.info(f"Analysis completed ✅ See: {self.output_dir}/results")
        shutil.rmtree(self.user_testing_review_dir)
