import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append('..')
from src.cli import main as cli

class TestMainFunction(unittest.TestCase):

    @patch('src.cli.ConfigManager')
    @patch('src.cli.Uploader')
    @patch('src.cli.TranscriptionJobMonitor')
    @patch('src.cli.Processor')
    @patch('src.cli.Summarizer')
    @patch('src.cli.Scorer')
    @patch('builtins.input', side_effect=['6'])  # To simulate quitting immediately
    def test_main_quit(self, mock_input, mock_scorer, mock_summarizer, mock_processor, mock_monitor, mock_uploader, mock_config_manager):
        with patch('builtins.print') as mock_print:
            cli()
            mock_print.assert_any_call("Exiting UXR Analysis Tool...")

    @patch('src.cli.ConfigManager.get_latest_output_dir')
    @patch('src.cli.ConfigManager.confirm_latest_output_dir', return_value=True)
    @patch('src.cli.Uploader')
    @patch('builtins.input', side_effect=['1', 'test_directory', '6'])  # Simulates choosing option 1 then quitting
    def test_main_upload(self, mock_input, mock_uploader, mock_confirm, mock_get_dir):
        mock_get_dir.return_value = "test_output_dir"
        cli()

        mock_uploader.assert_called_once_with('test_directory', 'test_output_dir')
        mock_uploader.return_value.upload_videos.assert_called_once()

    @patch('src.cli.ConfigManager.get_latest_output_dir')
    @patch('src.cli.ConfigManager.confirm_latest_output_dir', return_value=True)
    @patch('src.cli.TranscriptionJobMonitor')
    @patch('builtins.input', side_effect=['2', '6'])  # Simulates choosing option 2 then quitting
    def test_main_check_transcription(self, mock_input, mock_monitor, mock_confirm, mock_get_dir):
        mock_get_dir.return_value = "test_output_dir"
        cli()

        mock_monitor.assert_called_once_with('test_output_dir')
        mock_monitor.return_value.report_job_completion.assert_called_once()

    @patch('src.cli.ConfigManager.get_latest_output_dir')
    @patch('src.cli.ConfigManager.confirm_latest_output_dir', return_value=True)
    @patch('src.cli.Processor')
    @patch('builtins.input', side_effect=['3', '6'])  # Simulates choosing option 3 then quitting
    def test_main_process_transcripts(self, mock_input, mock_processor, mock_confirm, mock_get_dir):
        mock_get_dir.return_value = "test_output_dir"
        cli()

        mock_processor.assert_called_once_with('test_output_dir')
        mock_processor.return_value.process_transcripts.assert_called_once()

    @patch('src.cli.ConfigManager.get_latest_output_dir')
    @patch('src.cli.ConfigManager.confirm_latest_output_dir', return_value=True)
    @patch('src.cli.Summarizer')
    @patch('builtins.input', side_effect=['4', '6'])  # Simulates choosing option 4 then quitting
    def test_main_summarize_transcripts(self, mock_input, mock_summarizer, mock_confirm, mock_get_dir):
        mock_get_dir.return_value = "test_output_dir"
        cli()

        mock_summarizer.assert_called_once_with('test_output_dir')
        mock_summarizer.return_value.summarize_transcripts.assert_called_once()

    @patch('src.cli.ConfigManager.get_latest_output_dir')
    @patch('src.cli.ConfigManager.confirm_latest_output_dir', return_value=True)
    @patch('src.cli.Scorer')
    @patch('builtins.input', side_effect=['5', '6'])  # Simulates choosing option 5 then quitting
    def test_main_score_transcripts(self, mock_input, mock_scorer, mock_confirm, mock_get_dir):
        mock_get_dir.return_value = "test_output_dir"
        cli()

        mock_scorer.assert_called_once_with('test_output_dir')
        mock_scorer.return_value.score_results.assert_called_once()

if __name__ == '__main__':
    unittest.main()
