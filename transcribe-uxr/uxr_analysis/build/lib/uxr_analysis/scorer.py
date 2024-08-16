import os
import subprocess
import shutil
from datetime import datetime

class Scorer:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.results_dir = os.path.join(self.output_dir, "results")
        self.scores_dir = os.path.join(self.output_dir, "scores")
        self.reports = os.path.join(self.output_dir, "reports")

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
        rubric = """---
prompt: |
    Based on the feedback provided below, rate each of the following metrics on a scale of 1-100. Provide a specific fact-based justification for each score. Return the data in tabular format with columns for Rating Type, Score, and Justification.

    Metrics to rate:
    1. User Satisfaction
    2. Ease of Use
    3. Task Completion Rate
    4. Error Rate
    5. Time on Task
    6. Net Promoter Score (NPS)
    7. Usability Score
    8. Engagement Level
    9. Feature Discoverability
    10. Learnability
    11. User Feedback Sentiment
    12. System Usability Scale (SUS)
    13. Customer Effort Score (CES)
    14. Retention Rate
    15. Cognitive Load

    For each metric, provide the score and a justification in the following format:

    Rating Type | Score | Justification
    ------------|-------|--------------
    [Metric Name] | [1-100] | [Brief justification based on the feedback]

    Example:
    Rating Type | Score | Justification
    ------------|-------|--------------
    User Satisfaction | 90 | The participant stated the experience was "positive" and "helpful".
---
"""
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
                self.strip_graymatter(os.path.join(os.path.join(self.scores_dir, "02_scores.md")))
                with open(os.path.join(self.scores_dir, "01_feedback.md"), 'r') as summary_file:
                    summary_contents = summary_file.read()

                # Read scoring file
                with open(os.path.join(self.scores_dir, "02_scores.md"), 'r') as scoring_file:
                    scoring_contents = scoring_file.read()
                # Format the output
                formatted_output = f"""
# UXR Summary & Scoring Results [AI Generated] - {file_name}
The following is a summary and scoring of the audio from a user testing video on {datetime.now().strftime('%m/%d/%Y')}. 

## Summary
The following summary is based on the provided user test methodology
{summary_contents}

## Scoring
The following scores are based on the provided user test rubric.
{scoring_contents}
"""
                # Write to output file
                base_name = os.path.splitext(file_name)[0]
                reports_file_path = os.path.join(self.reports, f"{base_name}.md")
                with open(reports_file_path, 'w') as output_file:
                    output_file.write(formatted_output)
        print("✅ Done!")
    def score_results(self):
        self.process_feedback_files()
