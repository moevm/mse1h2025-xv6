import argparse
import os
import sys
import json
import re
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
REPORT_FILE = LOGS_DIR / f"{archive_name}.json"           

def parse_log_line(line):
    regex = r'([\d-]+\s[\d:,]+) - (\w+) - (.+)'
    match = re.match(regex, line.strip())
    if match:
        timestamp, level, message = match.groups()
        return {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
    else:
        return None

def main():
    '''Преобразование log-файла в формат .json'''
    with open(LOG_FILE, 'r', encoding='utf-8') as log_file_r:
        log_lines = log_file_r.readlines()

    log_entries = [parse_log_line(line) for line in log_lines if line.strip()]
    log_entries = [entry for entry in log_entries if entry is not None]
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as json_file:
        json.dump(log_entries, json_file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
