from pathlib import Path
import sys
import logging
import json

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
log_files_to_merge = ["load.log", "file_checker.log", "qemu-gdb.log"]

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
            

def analyze_log(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            logs = file.read()
            if "FAILED" in logs:
                return {"status": "FAIL", "score": 0}
            elif "PASSED" in logs:
                return {"status": "PASS", "score": 100}
            else:
                return {"status": "UNKNOWN", "score": 0}
    except FileNotFoundError:
        return {"status": "ERROR", "score": 0, "message": "test.log not found"}

def save_result(data, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

result = analyze_log(log_file)
save_result(result, report_file)
