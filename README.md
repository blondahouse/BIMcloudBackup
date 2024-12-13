# BIMcloud Backup Tool

## Overview

The BIMcloud Backup Tool is a Python-based solution designed to automate the backup process for projects hosted on Graphisoft BIMcloud. This tool enables seamless backups and integration with Google Drive or similar platforms for version control, ensuring project data is safeguarded and easily accessible.

---

## Features

- **Automated Backups**: Supports full backups, recently edited projects, or specific projects.
- **Customizable**: Configure target directories, tasks, and authentication details.
- **Centralized Logging**: Comprehensive logs for all actions, errors, and results.
- **Integration Ready**: Ideal for use with Google Drive or other file synchronization platforms.

---

## Target Audience

This tool is designed for **BIM Managers** and **IT Professionals** seeking to automate and streamline their BIMcloud backup processes.

---

## Prerequisites

- **Python Version**: 3.10 or newer.
- **Python Packages**:
  - `argparse`
  - `requests`
  - `shutil`
  - `datetime`
  - Additional dependencies listed in `requirements.txt`.
- Access to a Graphisoft BIMcloud Manager API.

---

## Installation

1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/your-repo/bimcloud-backup-tool.git
   ```
2. Navigate to the project directory:
   ```bash
   cd bimcloud-backup-tool
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Batch File Execution**:
   Create a `.bat` file similar to the example below:

   ```bat
    @echo off
    REM Example batch file to run BIMcloud Backup Script using Windows Task Scheduler
    
    REM Set the command prompt to use UTF-8
    chcp 65001 > NUL
    
    REM Define the path to the Python executable and the script location
    SET PYTHON_PATH=C:\path\to\python.exe
    SET SCRIPT_PATH=C:\path\to\bimcloud_backup\main.py
    
    REM Define arguments for the script
    SET MANAGER_URL=https://your-bimcloud-manager-url.com
    SET CLIENT_ID=your-client-id
    SET USERNAME=your-username
    SET PASSWORD=your-password
    REM Options: all, edited, selected
    SET TASK=all
    REM Optional: Set PROJECT_PATH to an empty string if TASK is not selected
    SET PROJECT_PATH=directory/filename
    REM Define the target root directory for copying backup files
    SET TARGET_ROOT=C:\path\to\target\directory
    
    REM Run the script with the defined arguments
    %PYTHON_PATH% %SCRIPT_PATH% -m %MANAGER_URL% -c %CLIENT_ID% -u %USERNAME% -p %PASSWORD% -t %TASK% -prj %PROJECT_PATH% -tgt %TARGET_ROOT%
    
    pause
   ```

2. **Run the Script**:
   Execute the batch file to start the backup process:
   ```bash
   double-click example.bat
   ```

3. **Command-line Execution**:
   Run the script with arguments:
   ```bash
   python main.py -m http://your-bimcloud-manager-url/ -c your-client-id -u your-username -p your-password -t all -tgt "C:\Path\To\Backup"
   ```

---

## Configuration

### Arguments
- `-m`, `--manager_url` *(required)*: BIMcloud Manager URL.
- `-c`, `--client_id` *(required)*: Client ID for authentication.
- `-u`, `--username` *(required)*: Username for authentication.
- `-p`, `--password` *(required)*: Password for authentication.
- `-t`, `--task` *(required)*: Task type (`all`, `edited`, `selected`).
- `-prj`, `--project_path` *(optional)*: Specific project path for the `selected` task.
- `-tgt`, `--target_root` *(required)*: Directory for storing backups.

---

## Project Structure

```plaintext
bimcloud_backup/
├── bimcloud_api/                # Copied and slightly modified Graphisoft API
├── bimcloud_custom/             # Custom module to extend the API
│   └── custom_managerapi.py
├── utils/                       # Utility functions
│   ├── logger.py                # Utility for handling logging.
│   └── file_utils.py            # Utility for handling file I/O.
├── backup_manager.py            # Main logic for managing backups.
├── main.py                      # Entry point script.
├── logs/                        # Log directory.
├── example.bat                  # Example batch file for Windows Task Scheduler.
└── README.md                    # Project documentation.
```

---

## Limitations and Future Improvements

- **Connection Handling**: The current script refreshes access tokens as required but could benefit from enhanced error handling.
- **OAuth2 Authentication**: Planned for future updates.
- **UI/UX**: Future iterations may include a user-friendly interface.
- **Data Collection for Analytics**: Future updates will include features to collect and visualize summary information about the backup process (successes/errors) and generate statistics on project usage and user activity.

---

## License

This project is licensed under the MIT License.

---

## Contribution

We welcome contributions to improve the tool. Feel free to submit issues or pull requests.

---

## Contact

For questions, issues, or suggestions, please contact blondahouse@gmail.com.
