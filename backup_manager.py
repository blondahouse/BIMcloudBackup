from utils.logger import setup_logger
import os
import time
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from bimcloud_custom.custom_managerapi import CustomManagerApi
from utils.file_utils import copy_file, check_file_update

# Define constants
BACKUP_FOLDER = 'Backups'
BACKUP_FILE_EXTENSION = '.archive'
PROJECT_ROOT = 'Project Root'


class BackupManager:
    def __init__(self, manager_url, username, password, client_id, task, project_path=None, target_root=None, file_extension=None):
        self.manager_url = manager_url
        self.username = username
        self.password = password
        self.client_id = client_id
        self.task = task
        self.project_path = project_path
        self.target_root = target_root
        self.file_extension = file_extension

        # Set up logger
        self.logger = setup_logger("backup_manager", f'{self.client_id}.log')
        self.logger.info("Initializing Backup Manager")

        # Initialize API connection
        self.api = CustomManagerApi(self.manager_url)
        self.auth_context = self.api.get_token_by_password_grant(self.username, self.password, self.client_id)

    def run_backup(self):
        self.logger.info("Backup process started.")
        try:
            projects = self.select_projects()
            self.logger.info(f"Number of projects selected for backup: {len(projects)}")
            for project in projects:
                self.backup_project(project)

            # After all backups are completed and copied, delete them from BIMcloud server
            self.delete_all_project_backups()
            self.delete_all_library_backups()

        except Exception as e:
            self.logger.error(f"Error during backup process: {e}")
        finally:
            self.logger.info("Backup process finished.")

    def select_projects(self):
        self.logger.info("Selecting projects for backup.")
        projects = self.api.get_projects(self.auth_context)
        self.logger.info(f"Total projects retrieved: {len(projects)}")

        if self.task == "all":
            return projects
        elif self.task == "edited":
            edited_projects = [project for project in projects if self.was_recently_edited(project)]
            self.logger.info(f"Number of projects edited in the last specified duration: {len(edited_projects)}")
            return edited_projects
        elif self.task == "selected":
            if not self.project_path:
                raise ValueError("Project path must be provided for the selected task type.")
            full_project_path = f"{PROJECT_ROOT}/{self.project_path}"
            selected_projects = [project for project in projects if project['$path'] == full_project_path]
            self.logger.info(
                f"Number of projects matching the selected path '{full_project_path}': {len(selected_projects)}")
            return selected_projects
        else:
            raise ValueError(f"Unknown task type: {self.task}")

    def was_recently_edited(self, project, duration_seconds=86400):
        """
        Determines if a project was edited within the given duration.

        Args:
            project (dict): The project dictionary containing metadata.
            duration_seconds (int): The duration in seconds to check for recent edits.

        Returns:
            bool: True if the project was edited within the specified duration, False otherwise.
        """
        now_date_utc = datetime.now().astimezone(timezone.utc).replace(tzinfo=None)
        last_edit_datetime = datetime.fromtimestamp(project["$modifiedDate"] / 1000).replace(tzinfo=None)
        recently_edited = (now_date_utc - last_edit_datetime).total_seconds() < duration_seconds
        self.logger.info(f"Project '{project['name']}' edited within {duration_seconds} seconds: {recently_edited}")
        return recently_edited

    def backup_project(self, project):
        project_name = project["name"]

        try:
            # Create backup
            resource_id, backup_name, backup_filename = self.create_bimproject_backup(project)

            # Get source and target paths
            source, target = self.get_backup_file_paths(project, backup_filename)

            # Copy the backup file
            copy_file(source, target)

            # Verify the backup file
            if not check_file_update(target):
                self.logger.warning(f"Backup verification failed for project '{project_name}'.")

            # Delete the backup
            self.delete_resource_backup_by_name(resource_id, backup_name)

        except Exception as e:
            self.logger.error(f"Error during backup process for project '{project_name}': {e}")

    def create_bimproject_backup(self, project):
        project_id = project["id"]
        project_name = project["name"]
        backup_type = 'bimproject'
        backup_name = f"{project_name}-{datetime.now().strftime('%y%m%d-%H%M%S')}"
        self.logger.info(f"Creating backup for project: {project_name}")

        job = self.api.create_resource_backup(self.auth_context, project_id, backup_type, backup_name)

        while job['status'] not in ['completed', 'failed']:
            time.sleep(1)
            job = self.api.get_job(self.auth_context, job['id'])

        if job['status'] == 'completed':
            resource_id = job["data"]["resourceId"]
            backups = self.api.get_resource_backups_by_criterion(self.auth_context, [resource_id], {}, {})
            backup_filename = ""
            for backup in backups:
                if backup['$name'] == backup_name:
                    backup_filename = (Path(PureWindowsPath(project['$pathOnServer']))
                                       / BACKUP_FOLDER / backup['$backupFileName'])
            self.logger.info(f"Backup completed for project: {project_name}")
            return resource_id, backup_name, backup_filename
        else:
            self.logger.error(f"Backup failed for project: {project_name}, Error: {job['result']}")
            raise RuntimeError("Backup job failed")

    def get_backup_file_paths(self, project, backup_filename):
        source = (Path(PureWindowsPath(project['$pathOnServer']))
                  / BACKUP_FOLDER / backup_filename)
        relative_path = PureWindowsPath(project['$path'][len(PROJECT_ROOT) + 1:])
        target = Path(self.target_root) / relative_path.with_suffix(self.file_extension)
        return source, target

    def delete_resource_backup_by_name(self, resource_id, backup_name):
        backups = self.api.get_resource_backups_by_criterion(self.auth_context, [resource_id], {}, {})
        for backup in backups:
            if backup['$name'] == backup_name:
                self.api.delete_resource_backup(self.auth_context, resource_id, backup['id'])
                self.logger.info(f"Deleted backup '{backup_name}' for resource ID {resource_id}")

    def delete_all_project_backups(self):
        self.logger.info("Deleting project backups.")
        try:
            backups = self.api.get_backups(self.auth_context)
            for backup in backups:
                if backup["$resourceType"] == "project":
                    resource_id = backup["$resourceId"]
                    backup_id = backup["id"]
                    self.api.delete_resource_backup(self.auth_context, resource_id, backup_id)
                    self.logger.info(f"Deleted backup with ID {backup_id} for project {resource_id}.")
        except Exception as e:
            self.logger.error(f"Error deleting project backups: {e}")

    def delete_all_library_backups(self):
        library_root_path = self.get_library_root_path()
        self.logger.info(f"Started deleting library backups in {library_root_path}.")

        try:
            for folder_name in os.listdir(library_root_path):
                folder_path = os.path.join(library_root_path, folder_name)

                if os.path.isdir(folder_path):
                    self.logger.info(f"Checking folder: {folder_path}")
                    backups_folder = os.path.join(folder_path, 'Backups')

                    if os.path.exists(backups_folder) and os.path.isdir(backups_folder):
                        self.logger.info(f"'Backups' folder found in {folder_path}")

                        try:
                            for file_name in os.listdir(backups_folder):
                                file_path = os.path.join(backups_folder, file_name)

                                if os.path.isfile(file_path):
                                    try:
                                        os.remove(file_path)
                                        self.logger.info(f"Deleted file: {file_path}")
                                    except Exception as e:
                                        self.logger.error(f"Failed to delete file {file_path}: {e}")
                                else:
                                    self.logger.warning(f"{file_path} is not a file. Skipping.")
                        except Exception as e:
                            self.logger.error(f"Failed to list contents of {backups_folder}: {e}")
                    else:
                        self.logger.info(f"No 'Backups' folder found in {folder_path}")
                else:
                    self.logger.warning(f"{folder_path} is not a directory. Skipping.")

        except Exception as e:
            self.logger.error(f"Error during the backup deletion process: {e}")

        self.logger.info("Finished deleting library backups.")

    def get_library_root_path(self):
        """
        Retrieves the root path of the library from the API.

        Returns:
            str: The root path of the library.
        """
        self.logger.info("Fetching library root path.")
        libraries = self.api.get_libraries(self.auth_context)
        if not libraries:
            raise ValueError("No libraries found in the BIMcloud.")

        library_path = libraries[0].get("$pathOnServer")
        if not library_path:
            raise ValueError("Library path is missing in the API response.")

        library_root_path = Path(library_path).parent
        self.logger.info(f"Library root path resolved: {library_root_path}")
        return str(library_root_path)
