import argparse
import os
import sys
import json
import re
from pathlib import Path

def parse_log_line(line):
    regex = r'([\d-]+\s[\d:,]+) - (\w+) - (.+)'
    match = re.match(regex, line.strip())
    if match:
        return {
            "timestamp": match.group(1),
            "level": match.group(2),
            "message": match.group(3)
        }
    return None

def main():
    parser = argparse.ArgumentParser(description='Generate test report')
    parser.add_argument('lab_branch', help='Lab branch name')
    parser.add_argument('archive', help='Path to zip archive')
    args = parser.parse_args()

    SCRIPT_DIR = Path(__file__).resolve().parent
    BASE_DIR = SCRIPT_DIR.parent
    LOGS_DIR = BASE_DIR / "logs"
    LOG_FILE = LOGS_DIR / f"{os.path.basename(args.archive)}.log"
    REPORT_FILE = LOGS_DIR / f"{os.path.basename(args.archive)}.json"

    print(f"Generating report from: {LOG_FILE}")
    print(f"Saving report to: {REPORT_FILE}")

    try:
        # Чтение с обработкой ошибок кодировки
        with open(LOG_FILE, 'r', encoding='utf-8', errors='replace') as f:
            log_entries = []
            for line in f:
                entry = parse_log_line(line)
                if entry:
                    log_entries.append(entry)

        # Запись отчета
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_entries, f, indent=2, ensure_ascii=False)
            print(f"Successfully wrote report to {REPORT_FILE}")

    except Exception as e:
        print(f"Error generating report: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
