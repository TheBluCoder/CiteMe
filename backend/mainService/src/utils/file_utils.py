import os
from src.config.log_config import setup_logging

filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)


class FileUtils:
    """
    A utility class providing static methods for common file operations.

    Class Attributes:
        ONE_MB (int): Constant representing one megabyte in bytes (1024 * 1024)
        MAX_FILE_SIZE (int): Maximum allowed file size (5 MB)
    """

    ONE_MB = 1024 * 1024
    MAX_FILE_SIZE = 5 * ONE_MB

    @staticmethod
    def check_file_exists(url: str, target_directory: str) -> str | bool:
        """
        Check if a file exists in the specified directory based on the URL.

        Args:
            url (str): The URL from which to extract the filename
            target_directory (str): The directory path to check for the file

        Returns:
            str | bool: Full path to the file if it exists, False otherwise or on error
        """

        try:
            filename = url.rstrip('/').split('/')[-1]
            full_path = os.path.join(target_directory, filename)
            return full_path if os.path.exists(full_path) else False
        except Exception as e:
            logger.exception(f"Error checking file existence: {e}")
            return False

    @staticmethod
    def ensure_directory(path: str) -> bool:
        """
        Ensure that a directory exists, creating it if necessary.

        Args:
            path (str): The directory path to create or verify

        Returns:
            bool: True if the directory exists or was created successfully,
                  False if an error occurred

        """

        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logger.exception(f"Error creating directory {path}: {e}")
            return False
