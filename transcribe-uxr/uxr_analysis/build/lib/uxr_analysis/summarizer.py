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

        aillyrc_content = (
            "You are a research analyst reviewing a user testing study conducted by the SDK Code Examples team at AWS. "
            "Your task is to generate insights based on how customers interact with code examples on the docs site and "
            "in GitHub, following the study steps provided in the template file."
        )
        self.create_file(os.path.join(self.user_testing_review_dir, '.aillyrc'), aillyrc_content)

        template_content = (
            "---\nprompt: >\n  You are tasked with summarizing a user testing study transcript conducted by the SDK Code Examples team at AWS. "
            "The study follows a specific set of steps, and participants were asked to comment or answer questions during each step. Your goal is to extract the participant's responses and comments for each step based on the context provided.\n\n"
            "  The template used for the study is as follows:\n\n"
            "  | Step | Description | Participant Comments |\n"
            "  |------|-------------|----------------------|\n"
            "  | 1 | Have you worked with any AWS SDKs before? | |\n"
            "  | 2 | Navigation | |\n"
            "  | 3 | Imagine you want to run a scenario \"Getting started with DynamoDB\". <br> 1. What are your thoughts on this page? <br> 2. What may be confusing or missing? <br> 3. Would you actually run the code? | |\n"
            "  | 4 | Do you want a runnable scenario? Would you prefer to cut and paste code instead? | |\n"
            "  | 5 | Try to run the scenario. | |\n"
            "  | 6 | Navigation | |\n"
            "  | 7 | Notice the blue box \"more on GitHub\". Did you take this path and why or why not? | |\n"
            "  | 8 | You are now on the README page. Share where you would go next in order to run the scenario. | |\n"
            "  | 9 | If you have not done so already, scroll down to the bottom for \"Get started using tables, items, and queries\" under Scenarios. Please click to see the examples. Share your thoughts. Do you feel they are too complex, too simple, or just right? | |\n"
            "  | 10 | How are/would you use the code? If you just want single API examples, does the scenario context help or hinder? | |\n"
            "  | 11 | Navigation | |\n"
            "  | 12 | Please share your thoughts on the \"Run the examples\" section towards the bottom of the page. | |\n"
            "  | 13 | 1. Do you have any suggestions? <br> 2. Do you consider cost/resource usage before running? <br> 3. Why do you think you would use an example like this? For specific answers or broadly learning? | |\n"
            "  | 14 | Through completing these tasks, what did you learn? Are you looking to learn more? | |\n"
            "  | 15 | If familiar with DynamoDB, do you find value in a basic tutorial? <br> If not, do you feel the examples shown were helpful and the right type of examples to understand the basics? | |\n"
            "  | Final Thoughts | |\n\n"
            "  To summarize the transcript effectively, you should:\n\n"
            "  Carefully read through the transcript while keeping the step-by-step structure of the study in mind.\n"
            "  For each step, identify the relevant sections in the transcript where the participant provided comments or answered questions.\n"
            "  Extract the participant's responses and comments verbatim, ensuring that you maintain the context and meaning accurately.\n"
            "  Organize the extracted responses and comments under the corresponding step from the template.\n"
            "  If a step does not have a clear response or comment from the participant, indicate that with a simple \"No response\" or \"Not addressed\" note.\n\n"
            "  Please note that some steps may not have explicit markers in the transcript, so you will need to rely on the context and flow of the conversation to determine the appropriate step.\n\n"
            "  Your summary should be a well-structured document that follows the template, making it easy for the SDK Code Examples team to understand the participant's feedback and experience during each step of the study.\n"
            "---"
        )
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
