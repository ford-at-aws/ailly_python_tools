
# UXR Transcript Wizard

A command-line application designed to upload user experience research (UXR) session videos to AWS S3, start transcription jobs using AWS Transcribe, and summarize and score the resulting transcripts.
## Features

- Upload UXR session videos to AWS S3.
- Start transcription jobs using AWS Transcribe.
- Monitor transcription job progress.
- Download and parse transcription results.
- Summarize parsed transcripts.
- Score summarized transcripts based on various usability metrics.
- Save configuration data to a file for easy management.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/uxr-analysis.git
    cd uxr-analysis
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Install the package:
    ```bash
    pip install .
    ```

## Usage

### 1. Running the Tool

To start the UXR Analysis Tool, simply run the `uxr_analysis` command:

```bash
uxr_analysis
```

This will display an ASCII art banner and provide you with a menu of options to choose from.

### 2. Uploading Videos

To upload videos and start transcription jobs, use the `upload` command. This command will prompt you to enter a name for the S3 bucket and will display a summary of the files to be processed.

```bash
uxr_analysis upload /path/to/video/directory
```

Example:

```bash
uxr_analysis upload ~/Downloads/video_archive
```

### 3. Checking Transcription Job Progress

To check the progress of transcription jobs, use the `monitor` command. This command will fetch and display the status of ongoing transcription jobs.

```bash
uxr_analysis monitor
```

### 4. Processing Transcripts

To process the transcripts, use the `process` command. This command will download the transcription results from S3 and parse them into readable text files.

```bash
uxr_analysis process
```

### 5. Summarizing Transcripts

To summarize the parsed transcripts, use the `summarize` command. This command will generate summaries of the transcripts based on a predefined template.

```bash
uxr_analysis summarize
```

### 6. Scoring Summarized Transcripts

To score the summarized transcripts, use the `score` command. This command will evaluate the transcripts based on various usability metrics.

```bash
uxr_analysis score
```

### 7. Exiting the Tool

To exit the UXR Analysis Tool, select the `Quit` option from the menu.

## Configuration

The application saves configuration data (such as the bucket name and file details) to a file called `uxr_config.json`. This file is used to store temporary data between the upload and process steps, allowing for a seamless workflow.

## Directory Structure

The UXR Analysis Tool organizes files and directories as follows:

- `transcripts/`: Directory for raw downloaded transcriptions.
- `parsed_transcriptions/`: Directory for parsed transcriptions.
- `results/`: Directory for storing summarized and scored results.
- `scores/`: Directory for storing scorecards.
- `reports/`: Directory for final reports.

## Logging

The tool logs various operations and errors, which can be useful for troubleshooting. The log level is set to `INFO` by default.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.
