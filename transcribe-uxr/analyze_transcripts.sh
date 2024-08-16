#!/bin/bash

# Check if parsed_transcripts directory is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <parsed_transcripts_directory>"
  exit 1
fi

# Get the parsed_transcripts directory
transcripts_dir="$1"
echo "Parsed transcripts directory: $transcripts_dir" # Log the parsed transcripts directory

# Create project directory
mkdir -p user_testing_review
echo "Creating project directory: user_testing_review" # Log directory creation

# Create results directory
mkdir -p results
echo "Creating results directory: results" # Log directory creation

# Create .aillyrc file
cat <<EOL > user_testing_review/.aillyrc
You are a research analyst reviewing a user testing study conducted by the SDK Code Examples team at AWS. Your task is to generate insights based on how customers interact with code examples on the docs site and in GitHub, following the study steps provided in the template file.
EOL
echo "Created .aillyrc file" # Log file creation

# Create template file
cat <<EOL > user_testing_review/10_template.md
---
prompt: >
  You are tasked with summarizing a user testing study transcript conducted by the SDK Code Examples team at AWS. The study follows a specific set of steps, and participants were asked to comment or answer questions during each step. Your goal is to extract the participant's responses and comments for each step based on the context provided.

  The template used for the study is as follows:

  | Step | Description | Participant Comments |
  |------|-------------|----------------------|
  | 1 | Have you worked with any AWS SDKs before? | |
  | 2 | Navigation | |
  | 3 | Imagine you want to run a scenario "Getting started with DynamoDB". <br> 1. What are your thoughts on this page? <br> 2. What may be confusing or missing? <br> 3. Would you actually run the code? | |
  | 4 | Do you want a runnable scenario? Would you prefer to cut and paste code instead? | |
  | 5 | Try to run the scenario. | |
  | 6 | Navigation | |
  | 7 | Notice the blue box "more on GitHub". Did you take this path and why or why not? | |
  | 8 | You are now on the README page. Share where you would go next in order to run the scenario. | |
  | 9 | If you have not done so already, scroll down to the bottom for "Get started using tables, items, and queries" under Scenarios. Please click to see the examples. Share your thoughts. Do you feel they are too complex, too simple, or just right? | |
  | 10 | How are/would you use the code? If you just want single API examples, does the scenario context help or hinder? | |
  | 11 | Navigation | |
  | 12 | Please share your thoughts on the "Run the examples" section towards the bottom of the page. | |
  | 13 | 1. Do you have any suggestions? <br> 2. Do you consider cost/resource usage before running? <br> 3. Why do you think you would use an example like this? For specific answers or broadly learning? | |
  | 14 | Through completing these tasks, what did you learn? Are you looking to learn more? | |
  | 15 | If familiar with DynamoDB, do you find value in a basic tutorial? <br> If not, do you feel the examples shown were helpful and the right type of examples to understand the basics? | |
  | Final Thoughts | |

  To summarize the transcript effectively, you should:
  
  Carefully read through the transcript while keeping the step-by-step structure of the study in mind.
  For each step, identify the relevant sections in the transcript where the participant provided comments or answered questions.
  Extract the participant's responses and comments verbatim, ensuring that you maintain the context and meaning accurately.
  Organize the extracted responses and comments under the corresponding step from the template.
  If a step does not have a clear response or comment from the participant, indicate that with a simple "No response" or "Not addressed" note.
  Please note that some steps may not have explicit markers in the transcript, so you will need to rely on the context and flow of the conversation to determine the appropriate step.

  Your summary should be a well-structured document that follows the template, making it easy for the SDK Code Examples team to understand the participant's feedback and experience during each step of the study.
---
EOL
echo "Created template file: user_testing_review/10_template.md" # Log file creation

# Iterate over all transcript files in the directory
for transcript_file in "$transcripts_dir"/*.json; do
  # Extract the base name of the transcript file
  transcript_basename=$(basename "$transcript_file" .json)
  echo "Processing transcript file: $transcript_file" # Log the transcript file being processed
  
  # Read the entire content of the transcript file
  transcript_text=$(cat "$transcript_file")

  # Create transcript file with extracted text
  cat <<EOL > "user_testing_review/20_${transcript_basename}.md"
---
prompt: >
  $transcript_text
---
EOL
  echo "Created transcript file: user_testing_review/20_${transcript_basename}.md" # Log file creation

  # Create analysis file for the transcript
  cat <<EOL > "user_testing_review/30_analysis_${transcript_basename}.md"
---
prompt: >
  Using the template and transcript provided, fill out the table with participant comments for each step. Add a extra column and add a summary of the commentary for each step.
---
EOL
  echo "Created analysis file: user_testing_review/30_analysis_${transcript_basename}.md" # Log file creation

  cd user_testing_review
  echo "Running Ailly for transcript: $transcript_basename" # Log the AI model run
  npx ailly
  
  # Copy the output file to the results directory and clean up.
  mv "30_analysis_${transcript_basename}.md.ailly.md" "../results/${transcript_basename}.md"
  echo "Copied output file to results directory: results/${transcript_basename}.md" # Log file copy
  rm 20*
  rm 30*
  
  # Go back to the original directory for the next iteration
  cd ..

done

echo "Analysis completed. Check the 'user_testing_review' and 'results' directories for output files." # Log analysis completion
rm -Rf user_testing_review # Clean up the project directory