import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigManager:
    @staticmethod
    def get_config_file(output_dir: str) -> str:
        """
        Get the path to the configuration file in the specified output directory.

        :param output_dir: The directory where the configuration file is stored.
        :return: The full path to the configuration file.
        """
        return os.path.join(output_dir, "uxr_config.json")

    @staticmethod
    def load_config(output_dir: str) -> dict:
        """
        Load configuration data from a JSON file in the specified output directory.

        :param output_dir: The directory where the configuration file is stored.
        :return: The configuration data as a dictionary.
        :raises FileNotFoundError: If the configuration file does not exist.
        :raises Exception: If there is an error reading the configuration file.
        """
        config_file = ConfigManager.get_config_file(output_dir)
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {config_file} not found.")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration file {config_file}: {e}")
            raise

    @staticmethod
    def save_config(data: dict, output_dir: str) -> None:
        """
        Save configuration data to a JSON file in the specified output directory.

        :param data: The configuration data to be saved, typically as a dictionary.
        :param output_dir: The directory where the configuration file will be saved.
        :raises Exception: If there is an error saving the configuration file.
        """
        config_file = ConfigManager.get_config_file(output_dir)
        # Convert datetime objects to strings
        for file_info in data.get("files", []):
            if "start_time" in file_info and isinstance(file_info["start_time"], datetime):
                file_info["start_time"] = file_info["start_time"].isoformat()

        try:
            with open(config_file, "w") as f:
                json.dump(data, f, indent=4)
            logger.info(f"Configuration data saved to {config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration file {config_file}: {e}")
            raise

    @staticmethod
    def confirm_latest_output_dir() -> bool:
        """
        Confirm if the user wants to use the latest output directory.

        :return: True if the user confirms to use the latest output directory, otherwise False.
        """
        latest_output_dir = ConfigManager.get_latest_output_dir()
        if latest_output_dir and os.path.exists(latest_output_dir):
            use_latest = (
                input(
                    f"Do you want to use the latest output directory ({latest_output_dir})? (yes/no): "
                )
                .strip()
                .lower()
            )
            return use_latest == "yes"
        return False

    @staticmethod
    def get_latest_output_dir() -> str:
        """
        Retrieve the latest output directory path from a central file.

        :return: The path to the latest output directory as a string, or None if not found.
        """
        latest_output_dir_file = "latest_output_dir.txt"
        if os.path.exists(latest_output_dir_file):
            with open(latest_output_dir_file, "r") as f:
                return f.read().strip()
        return None

    @staticmethod
    def update_latest_output_dir(output_dir: str) -> None:
        """
        Update the latest output directory path in a central file.

        :param output_dir: The new latest output directory path to be saved.
        """
        latest_output_dir_file = "latest_output_dir.txt"
        with open(latest_output_dir_file, "w") as f:
            f.write(output_dir)
        logger.info(f"Updated latest output directory to {output_dir}")
