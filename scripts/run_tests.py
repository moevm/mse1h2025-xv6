import os
import subprocess
import sys
import threading
import logging
from datetime import datetime
from subprocess import TimeoutExpired

TARGET_DIR = "../lab_ready"     # Папка, где ищем Makefile
COMMAND = ["make", "grade"]     # Команда для выполнения
LOG_FILE = "logs/qemu-gdb.log"  # Файл логов
START_LOGGING_STR = "make[1]: Leaving directory"  # Строка-триггер для логов

def setup_logging(log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

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
    script_dir = get_script_dir()
    log_path = os.path.join(os.path.abspath(os.path.join(script_dir, "..")), LOG_FILE)
    setup_logging(log_path)

    lab_ready_path = os.path.abspath(os.path.join(script_dir, TARGET_DIR))
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
                if START_LOGGING_STR in decoded:
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
