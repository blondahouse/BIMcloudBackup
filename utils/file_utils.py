import shutil
from pathlib import Path
from utils.logger import setup_logger
from datetime import datetime, timezone

logger = None  # Placeholder for the logger

def set_logger(client_id):
    global logger
    logger = setup_logger("backup_manager", f'{client_id}.log')


def copy_latest_file_by_extension(source_dir, target_dir, file_extension):
    """
    Copy the latest backup file from the source directory to the target directory.

    :param source_dir: Source directory where the backup files are stored
    :param target_dir: Target directory where the backup files should be copied
    :param file_extension: File extension of the backup files to be copied
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)

    # Ensure the source directory exists
    if not source_path.exists() or not source_path.is_dir():
        raise FileNotFoundError(f"Source directory does not exist: {source_path}")

    # Ensure the target directory exists
    target_path.mkdir(parents=True, exist_ok=True)

    # Find the latest backup file in the source directory
    backup_files = list(source_path.glob(f'*{file_extension}'))
    if not backup_files:
        raise FileNotFoundError(f"No backup files found in source directory: {source_path}")

    latest_backup_file = max(backup_files, key=lambda f: f.stat().st_mtime)

    # Copy the latest backup file to the target directory
    try:
        shutil.copy2(latest_backup_file, target_path / latest_backup_file.name)
        logger.info(f"Copied {latest_backup_file} to {target_path}")
    except Exception as e:
        logger.error(f"Error copying {latest_backup_file} to {target_path}: {e}")
        raise


def copy_file(source_path, target_path):
    """
    Copy a file from the source path to the target path.

    :param source_path: Full path to the source file.
    :param target_path: Full path to the destination file.
    """
    try:
        source = Path(source_path)
        target = Path(target_path)

        # Verify if the source file exists
        if not source.exists() or not source.is_file():
            logger.error(f"Source file does not exist: {source}")
            raise FileNotFoundError(f"Source file does not exist: {source}")

        # Ensure the target directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(source, target)
        logger.info(f"Copied file from {source} to {target}")
    except Exception as e:
        logger.error(f"Error copying file from {source_path} to {target_path}: {e}")
        raise


def check_file_update(file_path: Path, duration_seconds: int = 14400) -> bool:
    """
    Check if the specified file exists and was modified within the last given duration.

    Args:
        file_path (Path): The path to the file to check.
        duration_seconds (int): The time duration in seconds to check the file's modification time.

    Returns:
        bool: True if the file exists and was modified within the duration, False otherwise.
    """
    if file_path.exists():
        modification_time = datetime.fromtimestamp(file_path.stat().st_mtime, timezone.utc)
        time_since_modification = (datetime.now().astimezone(timezone.utc) - modification_time).total_seconds()
        if time_since_modification < duration_seconds:
            logger.info(f"File recently updated: {file_path}")
            return True
        else:
            logger.warning(f"File not updated within the last {duration_seconds / 3600:.1f} hours: {file_path}")
            return False
    else:
        logger.error(f"File does not exist: {file_path}")
        return False
