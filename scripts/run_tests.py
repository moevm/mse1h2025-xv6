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
    """
    Рекурсивно ищет директорию с Makefile
    """
    for dirpath, dirnames, filenames in os.walk(start_dir):
        if 'Makefile' in filenames:
            return dirpath
    return None

def read_stream(stream, stream_type, trigger_str):
    """
    Чтение вывода процесса и логирование
    """
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
    timeout = 300 # Таймаут процесса
    script_dir = get_script_dir()
    log_path = os.path.join(os.path.abspath(os.path.join(script_dir, "..")), LOG_FILE)
    setup_logging(log_path)
    
    # Поиск директории с Makefile
    lab_ready_path = os.path.abspath(os.path.join(script_dir, TARGET_DIR))
    makefile_dir = find_makefile_dir(lab_ready_path)
    
    if not makefile_dir:
        error_msg = f"Makefile not found {lab_ready_path}"
        # print(error_msg)
        logging.error(error_msg)
        sys.exit(1)
    
    # Переход в директорию с Makefile
    try:
        os.chdir(makefile_dir)
    except Exception as e:
        error_msg = f"Error switching to directory {makefile_dir}: {str(e)}"
        # print(error_msg)
        logging.error(error_msg)
        sys.exit(1)
    
    # print(f"Лог-файл: {log_path}\nWorking directory: {os.getcwd()}")
    
    try:
        # Заголовок запуска
        logging.info("Process started")
        proc = subprocess.Popen(COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Потоки для чтения вывода
        stdout_thread = threading.Thread(target=read_stream, args=(proc.stdout, "STDOUT", START_LOGGING_STR))
        stderr_thread = threading.Thread(target=read_stream, args=(proc.stderr, "STDERR", START_LOGGING_STR))
        
        stdout_thread.start()
        stderr_thread.start()
        
        # Ожидание процесса
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
        
        stdout_thread.join(timeout=1)
        stderr_thread.join(timeout=1)
    
    except KeyboardInterrupt:
        logging.warning("User interrupted execution")
        # print("\nUser interruption")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Critical error: {e}")
        # print(f"A critical error has occurred: {str(e)}")
        sys.exit(1)
    
    # Финальный статус
    exit_code = proc.returncode
    status = "TRUE" if exit_code == 0 else f"FALSE ({exit_code})"
    logging.info(f"Process finished with status: {status}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
