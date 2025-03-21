import os
import subprocess
import sys
import threading
from datetime import datetime
from subprocess import TimeoutExpired

TARGET_DIR = "../lab_ready"    # Папка, где ищем Makefile
COMMAND = ["make", "grade"]    # Команда для выполнения
LOG_FILE = "qemu-gdb.log"      # Файл логов
START_LOGGING_STR = "make[1]: выход из каталога"  # Строка-триггер для логов

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

def read_stream(stream, stream_type, log_file, trigger_str):
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
                log_file.write(f"[{datetime.now().isoformat()} {stream_type}] === LOGGING STARTED ===\n")
            continue

        if logging_enabled:
            log_entry = f"[{datetime.now().isoformat()} {stream_type}] {decoded_line}\n"
            log_file.write(log_entry)
            print(decoded_line)

def main():
    timeout = 300  # Таймаут процесса
    script_dir = get_script_dir()
    parent_dir = os.path.abspath(os.path.join(script_dir, ".."))  

    log_dir = os.path.join(parent_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, LOG_FILE)

    # Поиск директории с Makefile
    lab_ready_path = os.path.abspath(os.path.join(script_dir, TARGET_DIR))
    makefile_dir = find_makefile_dir(lab_ready_path)

    if not makefile_dir:
        error_msg = f"Makefile not found {lab_ready_path}"
        print(error_msg)
        with open(log_path, "a") as f:
            f.write(f"[ERROR] {datetime.now().isoformat()} {error_msg}\n")
        sys.exit(1)

    # Переход в директорию с Makefile
    try:
        os.chdir(makefile_dir)
    except Exception as e:
        error_msg = f"Error switching to directory {makefile_dir}: {str(e)}"
        print(error_msg)
        with open(log_path, "a") as f:
            f.write(f"[ERROR] {datetime.now().isoformat()} {error_msg}\n")
        sys.exit(1)

    print(f"Лог-файл: {log_path}\nWorking directory: {os.getcwd()}")

    try:
        with open(log_path, "a", buffering=1) as log_file:
            # Заголовок запуска
            log_file.write(f"\n{'='*50}\New start {datetime.now().isoformat()}\n{'='*50}\n")
            
            # Запуск процесса
            proc = subprocess.Popen(
                COMMAND,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Потоки для чтения вывода
            stdout_thread = threading.Thread(
                target=read_stream,
                args=(proc.stdout, "STDOUT", log_file, START_LOGGING_STR)
            )
            stderr_thread = threading.Thread(
                target=read_stream,
                args=(proc.stderr, "STDERR", log_file, START_LOGGING_STR)
            )
            
            stdout_thread.start()
            stderr_thread.start()

            # Ожидание процесса
            try:
                proc.wait(timeout=timeout)
            except TimeoutExpired:
                log_file.write(f"[TIMEOUT] {datetime.now().isoformat()} Timeout: 5 minutes\n")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except TimeoutExpired:
                    log_file.write(f"[FORCE KILL] {datetime.now().isoformat()}\n")
                    proc.kill()
                    proc.wait()

            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)

    except KeyboardInterrupt:
        with open(log_path, "a") as f:
            f.write(f"[INTERRUPTED] {datetime.now().isoformat()} User interrupted execution\n")
        print("\nUser interruption")
        sys.exit(1)
    except Exception as e:
        with open(log_path, "a") as f:
            f.write(f"[CRITICAL] {datetime.now().isoformat()} {str(e)}\n")
        print(f"A critical error has occurred: {str(e)}")
        sys.exit(1)

    # Финальный статус
    exit_code = proc.returncode
    status = "TRUE" if exit_code == 0 else f"FALSE ({exit_code})"
    with open(log_path, "a") as f:
        f.write(f"[FINISHED] {datetime.now().isoformat()} Finished with status: {status}\n")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
