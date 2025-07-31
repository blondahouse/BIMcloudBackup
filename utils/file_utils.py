import shutil
import os
import time
import traceback
from pathlib import Path, PurePath
from utils.logger import setup_logger
from datetime import datetime, timezone
from .gdrive import GoogleDriveAPI

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


def upload_file_to_gdrive(
        source_path,
        drive_root_id,
        drive_relative_path,
        drive_api=None,
        max_attempts=3,
        wait_seconds=30
):
    """
    Upload a file to Google Drive, creating the necessary folder structure.

    :param source_path: Full path to the source file.
    :param drive_root_id: Google Drive folder ID for the root of backups.
    :param drive_relative_path: Subfolder path in Google Drive (e.g. '2612_2_Tel_Aviv').
    :param drive_api: Optionally, a GoogleDriveAPI instance to reuse.
    :param max_attempts: Attempts to upload the file to Google Drive.
    :param wait_seconds: Waiting time between attempts.
    """
    try:
        source = Path(source_path)
        if not source.exists() or not source.is_file():
            logger.error(f"Source file does not exist: {source}")
            raise FileNotFoundError(f"Source file does not exist: {source}")

        # Use provided API instance or create new one
        if drive_api is None:
            drive_api = GoogleDriveAPI('credentials.json', 'token.json')

        # Split into folder path and filename
        rel_path = PurePath(drive_relative_path)
        folder_path = str(rel_path.parent)
        drive_filename = rel_path.name

        # 1. Ensure the full folder chain exists, get final folder ID
        try:
            logger.info(
                f"Preparing to create/find folder. Full target path: '{folder_path}', drive_root_id: '{drive_root_id}'")
            folder_id = drive_api.get_or_create_folder(folder_path, drive_root_id)
            logger.info(f"Google Drive folder '{drive_relative_path}' ready (ID: {folder_id})")
        except Exception as e:
            logger.error(
                f"Error during get_or_create_folder for path '{folder_path}' "
                f"under root ID '{drive_root_id}': {e}\n{traceback.format_exc()}"
            )

        # 2. Upload file to this folder, overwriting if exists
        for attempt in range(1, max_attempts + 1):
            try:
                file_id = drive_api.upload_file(
                    str(source),
                    folder_id=folder_id,
                    overwrite=True,
                    drive_filename=drive_filename
                )
                logger.info(f"Uploaded '{source}' to Google Drive folder '{drive_relative_path}' as file ID {file_id}")
                break  # Success!
            except Exception as e:
                logger.error(f"Upload attempt {attempt} failed: {e}")
                if attempt < max_attempts:
                    logger.info(f"Retrying in {wait_seconds} seconds...")
                    time.sleep(wait_seconds)
                else:
                    logger.error("Max upload attempts reached. Upload failed.")
                    raise

    except Exception as e:
        logger.error(f"Error uploading file to Google Drive: {e}")
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


def check_gdrive_file_update(
        drive_api,
        folder_id: str,
        local_file_path: Path,
        drive_filename: str = None,
        duration_seconds: int = 14400
) -> bool:
    """
    Check if the specified file exists on Google Drive in the target folder,
    and was modified (uploaded) within the last given duration.
    Optionally, compares file size as a strong verification.
    """
    if not local_file_path.exists():
        logger.error(f"Local file does not exist: {local_file_path}")
        return False

    if drive_filename is None:
        drive_filename = local_file_path.name

    # Find the file in the target folder
    file_info = drive_api.find_file(drive_filename, folder_id)
    if not file_info:
        logger.error(f"File '{drive_filename}' not found in Google Drive folder ID {folder_id}")
        return False

    # Check Google Drive file modification time
    gdrive_file = drive_api.service.files().get(
        fileId=file_info['id'],
        fields='size, modifiedTime'
    ).execute()
    gdrive_mtime = datetime.fromisoformat(gdrive_file['modifiedTime'].replace('Z', '+00:00'))
    time_since_modification = (datetime.now(timezone.utc) - gdrive_mtime).total_seconds()

    if time_since_modification > duration_seconds:
        logger.warning(
            f"GDrive file '{drive_filename}' in folder ID {folder_id} not updated within "
            f"the last {duration_seconds / 3600:.1f} hours (modified {gdrive_mtime})"
        )
        return False

    # Check file size match
    local_size = os.path.getsize(local_file_path)
    gdrive_size = int(gdrive_file['size'])
    if local_size != gdrive_size:
        logger.warning(
            f"Size mismatch: local '{local_file_path}' ({local_size} bytes) vs "
            f"GDrive '{drive_filename}' ({gdrive_size} bytes) in folder ID {folder_id}"
        )
        return False

    logger.info(
        f"Google Drive file '{drive_filename}' in folder ID {folder_id} "
        f"is present, recently updated, and size matches local file."
    )
    return True
