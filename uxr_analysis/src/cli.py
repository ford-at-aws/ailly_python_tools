from .processor import Processor
from .scorer import Scorer
from .summarizer import Summarizer
from .uploader import Uploader
from .monitor_transcription import TranscriptionJobMonitor
from .config_manager import ConfigManager
import time
import os

def main():
    ascii_art = '''\n
            ██    ██ ██   ██ ██████       █████  ███    ██  █████  ██      ██    ██ ███████ ██ ███████ 
            ██    ██  ██ ██  ██   ██     ██   ██ ████   ██ ██   ██ ██       ██  ██  ██      ██ ██      
            ██    ██   ███   ██████      ███████ ██ ██  ██ ███████ ██        ████   ███████ ██ ███████ 
            ██    ██  ██ ██  ██   ██     ██   ██ ██  ██ ██ ██   ██ ██         ██         ██ ██      ██ 
             ██████  ██   ██ ██   ██     ██   ██ ██   ████ ██   ██ ███████    ██    ███████ ██ ███████ 
            '''

    print(ascii_art)

    # Check for the latest output directory
    if ConfigManager.confirm_latest_output_dir():
        latest_output_dir = ConfigManager.get_latest_output_dir()
        print(f"Using the latest output directory: {latest_output_dir}")
    else:
        # Create a new output directory with the current timestamp
        timestamp = int(time.time())
        latest_output_dir = f"out-{timestamp}"
        os.makedirs(latest_output_dir)
        ConfigManager.update_latest_output_dir(latest_output_dir)
        print(f"Created new output directory: {latest_output_dir}")

    while True:
        print("\nUXR Analysis Tool")
        print("1. Upload videos and start transcription")
        print("2. Check transcription job progress")
        print("3. Downloads transcripts and extracts audio text")
        print("4. Summarize parsed transcripts")
        print("5. Score summarized transcripts")
        print("6. Quit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            uploader = Uploader(latest_output_dir)
            uploader.upload_videos()
        elif choice == "2":
            monitor = TranscriptionJobMonitor(latest_output_dir)
            monitor.report_job_completion()
        elif choice == "3":
            processor = Processor(latest_output_dir)
            processor.process_transcripts()
        elif choice == "4":
            summarizer = Summarizer(latest_output_dir)
            summarizer.summarize_transcripts()
        elif choice == "5":
            scorer = Scorer(latest_output_dir)
            scorer.score_results()
        elif choice == "6":
            print("Exiting UXR Analysis Tool...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
