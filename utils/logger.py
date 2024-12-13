import logging
import os


def setup_logger(logger_name="backup_manager", log_filename="backup_manager.log"):
    """
    Set up a centralized logger for the project.

    :param logger_name: Name of the logger (default is "backup_manager")
    :param log_filename: Name of the log file (default is "backup_manager.log")
    """
    # Create a logger instance
    logger = logging.getLogger(logger_name)

    # Prevent adding multiple handlers
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Set up console handler with a custom format
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        # Set up file handler to log debug messages to a file
        log_directory = os.path.join(os.path.dirname(__file__), '..', 'logs')

        # Ensure the logs directory exists
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        file_handler = logging.FileHandler(os.path.join(log_directory, log_filename), encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger
