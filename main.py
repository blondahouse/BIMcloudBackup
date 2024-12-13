import argparse
import sys
import io
from utils.logger import setup_logger
from backup_manager import BackupManager

# Ensure proper handling of Unicode in the command-line interface
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def main():
    # Set up logging
    logger = setup_logger("backup_manager", "backup_manager.log")

    # Argument parsing
    parser = argparse.ArgumentParser(description="BIMcloud Backup Script")
    parser.add_argument('-m', '--manager_url', required=True, help='URL of the BIMcloud Manager')
    parser.add_argument('-c', '--client_id', required=True, help='Client ID for BIMcloud')
    parser.add_argument('-u', '--username', required=True, help='Username for BIMcloud authentication')
    parser.add_argument('-p', '--password', required=True, help='Password for BIMcloud authentication')
    parser.add_argument('-t', '--task', required=True, choices=['all', 'edited', 'selected'], help='Backup task type')
    parser.add_argument('-prj', '--project_path', help='Optional: Path to a specific project to back up (for selected task)')
    parser.add_argument('-tgt', '--target_root', required=True, help='Target root directory for copying backup files')

    args = parser.parse_args()

    # Instantiate BackupManager with parsed arguments
    try:
        backup_manager = BackupManager(
            manager_url=args.manager_url,
            client_id=args.client_id,
            username=args.username,
            password=args.password,
            task=args.task,
            project_path=args.project_path,
            target_root=args.target_root
        )

        # Run the backup task
        backup_manager.run_backup()
    except Exception as e:
        logger.error(f"Error in main execution: {e}")


if __name__ == "__main__":
    main()
