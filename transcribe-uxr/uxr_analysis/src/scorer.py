import os
import subprocess
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class Scorer:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.results_dir = os.path.join(self.output_dir, "results")
        self.scores_dir = os.path.join(self.output_dir, "scores")
        self.reports = os.path.join(self.output_dir, "reports")
        self.rubric_file = os.path.join("templates", "rubric.txt")
        self.template_file = os.path.join("templates", "consolidated_report.j2")

        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader('templates'))

    def strip_graymatter(self, filepath):
        with open(filepath, 'r') as file:
            lines = file.readlines()

        inside_graymatter = False
        stripped_lines = []

        for line in lines:
            if line.strip() == '---':
                inside_graymatter = not inside_graymatter
                continue
            if not inside_graymatter:
                stripped_lines.append(line)

        with open(filepath, 'w') as file:
            file.writelines(stripped_lines)

    def process_feedback_files(self):
        # Load the rubric from the file
        with open(self.rubric_file, 'r') as file:
            rubric = file.read()

        os.makedirs(self.scores_dir, exist_ok=True)
        os.makedirs(self.reports, exist_ok=True)

        for file_name in os.listdir(self.results_dir):

            if file_name.endswith(".md"):
                print(f"Processing file: {file_name}")

                shutil.copy(os.path.join(self.results_dir, file_name), os.path.join(self.scores_dir, "01_feedback.md"))

                self.strip_graymatter(os.path.join(self.scores_dir, "01_feedback.md"))

                # Create scores rubric file
                scorecard_file_path = os.path.join(self.scores_dir, "02_scores.md")
                with open(scorecard_file_path, "w") as scores_file:
                    scores_file.write(rubric)

                current_dir = os.getcwd()
                os.chdir(self.scores_dir)
                print("⚙️ Running AI model: npx ailly --combined --model sonnet")
                subprocess.run(["npx", "ailly", "--combined", "--model", "sonnet"])
                os.chdir(current_dir)
                self.strip_graymatter(os.path.join(self.scores_dir, "02_scores.md"))

                with open(os.path.join(self.scores_dir, "01_feedback.md"), 'r') as summary_file:
                    summary_contents = summary_file.read()

                # Read scoring file
                with open(os.path.join(self.scores_dir, "02_scores.md"), 'r') as scoring_file:
                    scoring_contents = scoring_file.read()

                # Load and render the Jinja2 template
                template = self.env.get_template("consolidated_report.j2")
                formatted_output = template.render(
                    file_name=file_name,
                    date=datetime.now().strftime('%m/%d/%Y'),
                    summary_contents=summary_contents,
                    scoring_contents=scoring_contents
                )

                # Write to output file
                base_name = os.path.splitext(file_name)[0]
                reports_file_path = os.path.join(self.reports, f"{base_name}.md")
                with open(reports_file_path, 'w') as output_file:
                    output_file.write(formatted_output)

        print("✅ Done!")

    def score_results(self):
        self.process_feedback_files()
