from pathlib import Path
import sys
import logging
import json
import re

# Пути к дирректориям
script_dir = Path(__file__).resolve().parent
base_dir = script_dir.parent
logs_dir = base_dir / "logs"

# log-файл и report-файл
# Если не передать аргумент, то файл с логами будет называться 'generate_report.log'
arguments = sys.argv
script_name = arguments[0]
if len(arguments) < 1:
    arguments.push("generate_report")
log_name = arguments[1] + ".log"
report_name = arguments[1] + ".json"
log_file = logs_dir / log_name
report_file = logs_dir / report_name

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),  # перезаписывать каждый запуск
        # logging.StreamHandler(sys.stdout) # It is just superfluous
    ]
)

# Список log-файлов для объединение в log_file
log_files_to_merge = ["load.log", "file_checker.log", "qemu-gdb.log", "error.log"]

# Открытие log_file на запись и добавление содержимого других логов
with open(log_file, 'w') as output_log:
    for file in log_files_to_merge:
        if file == "file_checker.log":
            output_log.write("\nTrivial checks:\n")
        elif file == "qemu-gdb.log":
            output_log.write("\nChecking the performance of laboratory work:\n")
        file_path = logs_dir / file
        try:
            with open(file_path, 'r') as input_log:
                output_log.write(input_log.read())
        except FileNotFoundError:
            logging.warning(f"File {file} is not found")
        except Exception as e:
            logging.error(f"Error while reading {file}: {e}")
            

# Преобразование log-файла в формат .json
with open(log_file, 'r', encoding='utf-8') as log_file_r:
    log_lines = log_file_r.readlines()

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

log_entries = [parse_log_line(line) for line in log_lines if line.strip()]
log_entries = [entry for entry in log_entries if entry is not None]

with open(report_file, 'w', encoding='utf-8') as json_file:
    json.dump(log_entries, json_file, ensure_ascii=False, indent=4)
