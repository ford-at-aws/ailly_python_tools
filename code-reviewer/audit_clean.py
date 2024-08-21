import logging
import os
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def list_temp_directories() -> list:
    """
    List all directories with the 'tmp_' prefix.

    Returns:
        list: A list of paths to directories with the 'tmp_' prefix.
    """
    return [d for d in os.listdir() if os.path.isdir(d) and d.startswith("tmp_")]


def get_creation_time(directory: str) -> float:
    """
    Get the creation time of a directory.

    Args:
        directory (str): The directory path.

    Returns:
        float: The creation time of the directory.
    """
    return os.path.getctime(directory)


def clean_old_directories() -> None:
    """
    Remove all but the most recently created 'tmp_' directories.
    """
    temp_dirs = list_temp_directories()

    if not temp_dirs:
        logging.info("No temporary directories found.")
        return

    # Sort directories by their creation time
    temp_dirs.sort(key=get_creation_time, reverse=True)

    # Keep the most recent directory and remove the others
    directories_to_remove = temp_dirs[1:]

    if not directories_to_remove:
        logging.info("Only one temporary directory exists. No cleanup necessary.")
        return

    for dir_to_remove in directories_to_remove:
        try:
            shutil.rmtree(dir_to_remove)
            logging.info(f"Removed directory: {dir_to_remove}")
        except Exception as e:
            logging.error(f"Failed to remove directory {dir_to_remove}: {e}")


def main() -> None:
    """
    Main function to execute the cleanup.
    """
    clean_old_directories()


if __name__ == "__main__":
    main()
