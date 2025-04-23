import argparse
import os
import subprocess
import sys
import threading
import logging
from pathlib import Path
from datetime import datetime
from subprocess import TimeoutExpired

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

'''TARGET'''
TARGET_DIR = "../lab_ready"     # Папка, где ищем Makefile
COMMAND = ["make", "grade"]     # Команда для выполнения
# Строки-триггеры для логов
START_LOGGING_STR_EN = "make[1]: Leaving directory"
START_LOGGING_STR_RU = "make[1]: выход из каталога"

def setup_logging(log_path):
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.info("\n\nChecking the performance of laboratory work:")

def find_makefile_dir(start_dir):
    for dirpath, dirnames, filenames in os.walk(start_dir):
        if 'Makefile' in filenames:
            return dirpath
    return None

def read_stream(stream, stream_type, trigger_str):
    trigger_count = 0
    logging_enabled = False

    while True:
        line = stream.readline()
        if not line:
            break
        decoded_line = line.decode(errors='replace').rstrip()

        # Включение логирования после двух появлений триггера
        if trigger_str in decoded_line:
            trigger_count += 1
            if trigger_count == 2:
                logging_enabled = True
                logging.info("=== LOGGING STARTED ===")
            continue

        if logging_enabled:
            if stream_type == "STDERR":
                logging.error(decoded_line)
            else:
                logging.info(decoded_line)
            # print(decoded_line)

def main():
    timeout = 300  # Таймаут процесса
    setup_logging(LOG_FILE)

    lab_ready_path = os.path.abspath(os.path.join(SCRIPT_DIR, TARGET_DIR))
    makefile_dir = find_makefile_dir(lab_ready_path)

    if not makefile_dir:
        logging.error(f"Makefile not found {lab_ready_path}")
        sys.exit(1)

    try:
        os.chdir(makefile_dir)
    except Exception as e:
        logging.error(f"Error switching to directory {makefile_dir}: {str(e)}")
        sys.exit(1)

    try:
        logging.info("Process started")
        proc = subprocess.Popen(COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout_lines = []
        stderr_lines = []

        def read_and_store(stream, stream_type):
            trigger_count = 0
            logging_enabled = False

            for line in iter(stream.readline, b''):
                decoded = line.decode(errors='replace').rstrip()
                if (START_LOGGING_STR_EN in decoded) or (START_LOGGING_STR_RU in decoded):
                    trigger_count += 1
                    if trigger_count == 2:
                        logging_enabled = True
                        logging.info("=== LOGGING STARTED ===")
                    continue

                if logging_enabled:
                    if stream_type == "STDOUT":
                        logging.info(decoded)
                    else:
                        logging.error(decoded)

                if stream_type == "STDOUT":
                    stdout_lines.append(decoded)
                else:
                    stderr_lines.append(decoded)

        t_out = threading.Thread(target=read_and_store, args=(proc.stdout, "STDOUT"))
        t_err = threading.Thread(target=read_and_store, args=(proc.stderr, "STDERR"))

        t_out.start()
        t_err.start()

        try:
            proc.wait(timeout=timeout)
        except TimeoutExpired:
            logging.critical("Timeout: 5 minutes")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except TimeoutExpired:
                logging.critical("Force kill executed")
                proc.kill()
                proc.wait()

        t_out.join(timeout=1)
        t_err.join(timeout=1)

        exit_code = proc.returncode

        if exit_code != 0:
            all_output = "\n".join(stdout_lines + stderr_lines)
            if "Score" in all_output:
                exit_code = 0

        status = "TRUE" if exit_code == 0 else f"FALSE ({exit_code})"
        logging.info(f"Process finished with status: {status}")
        sys.exit(exit_code)

    except KeyboardInterrupt:
        logging.warning("User interrupted execution")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
