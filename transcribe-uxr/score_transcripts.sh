#!/bin/bash

# Create a directory to store all scores
mkdir all_scores

# Create a directory to temporarily store results
mkdir -p scores

# Copy results to the temporary scores directory
cp -R results scores/
cd scores

# Feedback prompt for the AI model
feedback="""---
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
    User Satisfaction | 90 | The participant found the overall experience positive and helpful.
---
"""

# Iterate over all files in the directory
for FILE in results/*.md; do
  if [ -f "$FILE" ]; then
    BASE_NAME=$(basename "$FILE" .md)
    NEW_NAME="01_feedback.md"
    echo "Processing file: $FILE" # Log the file being processed

    echo "$feedback" > "$NEW_NAME"
    sed -n '/^---$/,/^---$/!p' "$FILE" >> "$NEW_NAME"
    EXPORT_FILE="../all_scores/$BASE_NAME.md"
    printf '%s\n%s\n%s\n' "# Summarized transcript - $BASE_NAME" "## Summary of findings" > $EXPORT_FILE
    sed -n '/^---$/,/^---$/!p' "$FILE" >> $EXPORT_FILE
    echo "Running AI model: npx ailly --combined --model sonnet" # Log the AI model being run
    npx ailly --combined --model sonnet
    printf '%s\n%s\n%s\n' "## Scoring" >> $EXPORT_FILE
    sed -n '/^---$/,/^---$/!p' "$NEW_NAME" >> $EXPORT_FILE
  fi
done

cd ..
echo "Cleaning up temporary directory" # Log the cleanup process
rm -Rf scores