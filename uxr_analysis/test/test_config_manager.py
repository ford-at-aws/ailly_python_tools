import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
from datetime import datetime
from src.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):

    @patch("uxr_analysis.config_manager.os.path.join", return_value="mocked_path/uxr_config.json")
    def test_get_config_file(self, mock_path_join):
        output_dir = "mocked_path"
        config_file = ConfigManager.get_config_file(output_dir)
        self.assertEqual(config_file, "mocked_path/uxr_config.json")
        mock_path_join.assert_called_once_with(output_dir, "uxr_config.json")

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"key": "value"}))
    @patch("uxr_analysis.config_manager.ConfigManager.get_config_file", return_value="mocked_path/uxr_config.json")
    def test_load_config_success(self, mock_get_config_file, mock_open_file):
        output_dir = "mocked_path"
        config = ConfigManager.load_config(output_dir)
        self.assertEqual(config, {"key": "value"})
        mock_get_config_file.assert_called_once_with(output_dir)
        mock_open_file.assert_called_once_with("mocked_path/uxr_config.json", "r")

    @patch("builtins.open", side_effect=FileNotFoundError)
    @patch("uxr_analysis.config_manager.ConfigManager.get_config_file", return_value="mocked_path/uxr_config.json")
    @patch("uxr_analysis.config_manager.logger.error")
    def test_load_config_file_not_found(self, mock_logger_error, mock_get_config_file, mock_open_file):
        output_dir = "mocked_path"
        with self.assertRaises(FileNotFoundError):
            ConfigManager.load_config(output_dir)
        mock_logger_error.assert_called_once_with("Configuration file mocked_path/uxr_config.json not found.")

    @patch("builtins.open", new_callable=mock_open)
    @patch("uxr_analysis.config_manager.ConfigManager.get_config_file", return_value="mocked_path/uxr_config.json")
    @patch("uxr_analysis.config_manager.logger.info")
    def test_save_config_success(self, mock_logger_info, mock_get_config_file, mock_open_file):
        output_dir = "mocked_path"
        data = {"files": [{"start_time": datetime(2023, 1, 1, 12, 0)}]}
        ConfigManager.save_config(data, output_dir)

        mock_get_config_file.assert_called_once_with(output_dir)
        mock_open_file.assert_called_once_with("mocked_path/uxr_config.json", "w")
        mock_logger_info.assert_called_once_with("Configuration data saved to mocked_path/uxr_config.json")

        # Verify the JSON data written to the file
        written_data = json.loads(mock_open_file().write.call_args[0][0])
        self.assertEqual(written_data["files"][0]["start_time"], "2023-01-01T12:00:00")

    @patch("builtins.open", side_effect=Exception("Save error"))
    @patch("uxr_analysis.config_manager.ConfigManager.get_config_file", return_value="mocked_path/uxr_config.json")
    @patch("uxr_analysis.config_manager.logger.error")
    def test_save_config_exception(self, mock_logger_error, mock_get_config_file, mock_open_file):
        output_dir = "mocked_path"
        data = {"key": "value"}
        with self.assertRaises(Exception):
            ConfigManager.save_config(data, output_dir)
        mock_logger_error.assert_called_once_with(
            "Error saving configuration file mocked_path/uxr_config.json: Save error")

    @patch("uxr_analysis.config_manager.ConfigManager.get_latest_output_dir", return_value="mocked_dir")
    @patch("uxr_analysis.config_manager.os.path.exists", return_value=True)
    @patch("builtins.input", return_value="yes")
    def test_confirm_latest_output_dir_yes(self, mock_input, mock_exists, mock_get_latest):
        result = ConfigManager.confirm_latest_output_dir()
        self.assertTrue(result)
        mock_get_latest.assert_called_once()
        mock_exists.assert_called_once_with("mocked_dir")
        mock_input.assert_called_once_with("Do you want to use the latest output directory (mocked_dir)? (yes/no): ")

    @patch("uxr_analysis.config_manager.ConfigManager.get_latest_output_dir", return_value="mocked_dir")
    @patch("uxr_analysis.config_manager.os.path.exists", return_value=True)
    @patch("builtins.input", return_value="no")
    def test_confirm_latest_output_dir_no(self, mock_input, mock_exists, mock_get_latest):
        result = ConfigManager.confirm_latest_output_dir()
        self.assertFalse(result)
        mock_get_latest.assert_called_once()
        mock_exists.assert_called_once_with("mocked_dir")
        mock_input.assert_called_once_with("Do you want to use the latest output directory (mocked_dir)? (yes/no): ")

    @patch("uxr_analysis.config_manager.os.path.exists", return_value=False)
    @patch("uxr_analysis.config_manager.ConfigManager.get_latest_output_dir")
    def test_confirm_latest_output_dir_not_exists(self, mock_get_latest, mock_exists):
        result = ConfigManager.confirm_latest_output_dir()
        self.assertFalse(result)
        mock_get_latest.assert_called_once()
        mock_exists.assert_called_once_with(mock_get_latest.return_value)

    @patch("builtins.open", new_callable=mock_open, read_data="mocked_dir")
    @patch("uxr_analysis.config_manager.os.path.exists", return_value=True)
    def test_get_latest_output_dir_exists(self, mock_open_file, mock_exists):
        latest_dir = ConfigManager.get_latest_output_dir()
        self.assertEqual(latest_dir, "mocked_dir")
        mock_open_file.assert_called_once_with("latest_output_dir.txt", "r")
        mock_exists.assert_called_once_with("latest_output_dir.txt")

    @patch("uxr_analysis.config_manager.os.path.exists", return_value=False)
    def test_get_latest_output_dir_not_exists(self, mock_exists):
        latest_dir = ConfigManager.get_latest_output_dir()
        self.assertIsNone(latest_dir)
        mock_exists.assert_called_once_with("latest_output_dir.txt")

    @patch("builtins.open", new_callable=mock_open)
    @patch("uxr_analysis.config_manager.logger.info")
    def test_update_latest_output_dir(self, mock_logger_info, mock_open_file):
        output_dir = "mocked_dir"
        ConfigManager.update_latest_output_dir(output_dir)
        mock_open_file.assert_called_once_with("latest_output_dir.txt", "w")
        mock_open_file().write.assert_called_once_with(output_dir)
        mock_logger_info.assert_called_once_with(f"Updated latest output directory to {output_dir}")


if __name__ == '__main__':
    unittest.main()
