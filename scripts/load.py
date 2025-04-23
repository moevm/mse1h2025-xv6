import argparse
import os
import re
import sys
import tempfile
import zipfile
import shutil
import subprocess
import logging
from pathlib import Path

'''parser'''
parser = argparse.ArgumentParser(description='Apply student patch to xv6 lab repository.')
parser.add_argument('lab_branch', help='Lab branch name (e.g., util, syscall, thread, etc.)')
parser.add_argument('archive', help='Path to the zip archive containing patch file')
args = parser.parse_args()

lab_branch = args.lab_branch
archive_path = Path(args.archive)
archive_name = os.path.basename(archive_path)

'''SCRIPT_DIR, BASE_DIR, LOGS_DIR, LOG_FILE'''
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)  # создаём папку logs, если нет

LOG_FILE = LOGS_DIR / f"{archive_name}.log"

'''REPO'''
XV6_REPO_URL = "git://g.csail.mit.edu/xv6-labs-2024"
XV6_REPO_DIR = SCRIPT_DIR.parent / 'lab_ready' / 'xv6-labs-2024'

PATCH_DEST_DIR = SCRIPT_DIR.parent / 'lab_ready'
PATCH_DEST_DIR.mkdir(parents=True, exist_ok=True)

LAB_BRANCH_MAPPING = {
    'util': 'util',
    'syscall': 'syscall',
    'pgtbl': 'pgtbl',
    'traps': 'traps',
    'cow': 'cow',
    'thread': 'thread',
    'net': 'net',
    'lock': 'lock',
    'fs': 'fs',
    'mmap': 'mmap',
}

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, mode='w'),  # перезаписывать каждый запуск
        ]
    )
    logging.info(f"Logging to {LOG_FILE}")

def clone_xv6_repo():
    """Клонирует репозиторий xv6, если он ещё не существует"""
    if XV6_REPO_DIR.exists():
        logging.info("xv6 repository already exists")
        return True
    
    logging.info(f"Cloning xv6 repository from {XV6_REPO_URL}")
    try:
        subprocess.run(
            ['git', 'clone', XV6_REPO_URL, str(XV6_REPO_DIR)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.info("Successfully cloned xv6 repository")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to clone xv6 repository: {e.stderr}")
        return False

def checkout_lab_branch(branch_name):
    """Переключается на ветку лабы"""
    logging.info(f"Checking out lab branch: {branch_name}")
    try:
        result = subprocess.run(
            ['git', 'show-ref', '--verify', f'refs/heads/{branch_name}'],
            cwd=XV6_REPO_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logging.error(f"Branch {branch_name} doesn't exist in the repository")
            return False
        
        subprocess.run(
            ['git', 'checkout', branch_name],
            cwd=XV6_REPO_DIR,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=XV6_REPO_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        commit_hash = result.stdout.strip()
        logging.info(f"Checked out branch {branch_name}, commit: {commit_hash}")
        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to checkout branch {branch_name}: {e.stderr}")
        return False

def extract_patch_from_archive(archive_path):
    """Извлекает patch файл из архива в lab_ready"""
    logging.info(f"Extracting patch from archive: {archive_path}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with zipfile.ZipFile(archive_path, 'r') as archive:
                archive.extractall(temp_dir)
            
            for ext in ('*.patch', '*.diff'):
                files = list(Path(temp_dir).rglob(ext))
                if files:
                    patch_file = files[0]
                    if patch_file.stat().st_size == 0:
                        logging.error("Found empty patch file!")
                        return None
                    
                    dest_patch = PATCH_DEST_DIR / patch_file.name
                    shutil.copy(patch_file, dest_patch)
                    logging.info(f"Copied patch to: {dest_patch}")
                    return dest_patch

            logging.error("No patch file found in archive!")
            return None

        except zipfile.BadZipFile:
            logging.error("Invalid zip archive!")
            return None
        except Exception as e:
            logging.error(f"Error extracting archive: {e}")
            return None

def apply_patch(patch_file):
    """Применяет патч к репозиторию xv6"""
    logging.info(f"Applying patch {patch_file} to xv6 repository")
    
    try:
        check_cmd = ['git', 'apply', '--check', str(patch_file)]
        result = subprocess.run(
            check_cmd,
            cwd=XV6_REPO_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logging.error(f"Patch check failed: {result.stderr.strip()}")
            return False
        
        apply_cmd = ['git', 'apply', str(patch_file)]
        result = subprocess.run(
            apply_cmd,
            cwd=XV6_REPO_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            logging.info("Patch applied successfully")
            return True
        
        logging.error(f"Failed to apply patch: {result.stderr.strip()}")
        return False

    except Exception as e:
        logging.error(f"Error applying patch: {e}")
        return False

def check_makefile_changed(patch_file):
    """Проверяет, изменяется ли Makefile в патче"""
    logging.info(f"Checking if Makefile is modified in patch: {patch_file}")
    try:
        result = subprocess.run(
            ['git', 'apply', '--stat', str(patch_file)],
            cwd=XV6_REPO_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            logging.error(f"Failed to analyze patch: {result.stderr.strip()}")
            return False

        changed_files = result.stdout
        logging.info("Patch affects the following files:\n" + changed_files)

        if 'Makefile' in changed_files:
            logging.info("Makefile is modified by the patch.")
            return True
        else:
            logging.error("Add your sleep program to UPROGS in Makefile; once you've done that, make qemu will compile your program and you'll be able to run it from the xv6 shell.")
            return False

    except Exception as e:
        logging.error(f"Error checking Makefile modification: {e}")
        return False

def main():
    setup_logging()
    
    if not archive_path.is_file():
        logging.error(f"Archive not found: {archive_path}")
        sys.exit(1)

    logging.info(f"Using provided lab branch: {lab_branch}")

    patch_file = extract_patch_from_archive(archive_path)
    if not patch_file:
        logging.error("Failed to extract patch file from archive")
        sys.exit(1)

    if not clone_xv6_repo():
        sys.exit(1)

    if not checkout_lab_branch(lab_branch):
        sys.exit(1)

    if not apply_patch(patch_file):
        logging.error("Failed to apply patch. Exiting.")
        sys.exit(1)

    if not check_makefile_changed(patch_file):
        logging.error("Patch does not change the Makefile. Exiting.")
        sys.exit(1)

    logging.info(f"Successfully applied patch to xv6 repository at {XV6_REPO_DIR}")
    logging.info(f"Lab branch: {lab_branch}")
    logging.info("You can now run the lab tests in the xv6 repository")

if __name__ == '__main__':
    main()
