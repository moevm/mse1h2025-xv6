import argparse
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

def setup_logging(log_path):
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info(f"\n\nTrivial checks:\nLogging started. Logs are saved to: {log_path}")

def check_encoding(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            f.read()
        return True, ""
    except UnicodeDecodeError:
        return False, f"Error: file '{file_path}' is not in 'utf-8' encoding."

def check_size(file_path, max_size_mb=1):
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    if file_size > max_size_mb:
        return False, f"Error: file '{file_path}' exceeds the maximum size of {max_size_mb} MB."
    return True, ""

def check_extension(file_path, valid_extensions):
    _, ext = os.path.splitext(file_path)
    if ext not in valid_extensions:
        return False, f"Error: file '{file_path}' has an invalid extension '{ext}'. Expected: {', '.join(valid_extensions)}."
    return True, ""

def validate_files(lab_ready_path, valid_extensions, logger, max_size_mb=10):
    errors = []
    user_dirs_checked = 0
    files_checked = 0

    for dirpath, dirnames, filenames in os.walk(lab_ready_path):
        if os.path.basename(dirpath) == 'user':
            user_dirs_checked += 1
            logger.info(f"\nChecking folder: {dirpath}")

            for filename in filenames:
                files_checked += 1
                file_path = os.path.join(dirpath, filename)
                logger.info(f"Checking file: {file_path}")

                is_valid_encoding, encoding_error = check_encoding(file_path)
                if not is_valid_encoding:
                    logger.error(encoding_error)
                    errors.append(encoding_error)

                is_valid_size, size_error = check_size(file_path, max_size_mb)
                if not is_valid_size:
                    logger.error(size_error)
                    errors.append(size_error)

                is_valid_extension, extension_error = check_extension(file_path, valid_extensions)
                if not is_valid_extension:
                    logger.error(extension_error)
                    errors.append(extension_error)

    return errors, user_dirs_checked, files_checked

def main():
    parser = argparse.ArgumentParser(description='Validate lab files.')
    parser.add_argument('lab_branch', help='Lab branch name')
    parser.add_argument('archive', help='Path to the zip archive')
    args = parser.parse_args()

    BASE_DIR = Path(__file__).resolve().parent.parent
    lab_ready_path = BASE_DIR / 'lab_ready'

    if not lab_ready_path.exists():
        print(f"Folder lab_ready not found at path: {lab_ready_path}")
        sys.exit(1)

    LOGS_DIR = BASE_DIR / "logs"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE = LOGS_DIR / f"{os.path.basename(args.archive)}.log"

    setup_logging(LOG_FILE)
    logger = logging.getLogger()

    valid_extensions = ['.c', '.h', '.txt', '.py', '.S', '.ld', '.pl', '.sh']
    errors, user_dirs, files = validate_files(lab_ready_path, valid_extensions, logger)

    logger.info(f"Summary: checked {user_dirs} folders, {files} files. Errors: {len(errors)}")
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
