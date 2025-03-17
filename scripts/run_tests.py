import os
import subprocess
import sys
import threading
from datetime import datetime
from subprocess import TimeoutExpired


TARGET_DIR = "../xv6-labs-2024"    # Целевая директория для выполнения команд
COMMAND = ["make", "grade"]        # Команда для выполнения
LOG_FILE = "qemu-gdb.log"          # Имя файла для записи логов
START_LOGGING_STR = "make[1]: выход из каталога"  # Строка-триггер для начала логирования


def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def read_stream(stream, stream_type, log_file, trigger_str):
    """
    Чтение потока вывода процесса
    :param stream: Поток вывода (stdout/stderr)
    :param stream_type: Тип потока для маркировки
    :param log_file: Файловый объект для записи логов
    :param trigger_str: Строка-триггер для активации логирования
    """
    trigger_count = 0
    logging_enabled = False

    while True:
        line = stream.readline()
        if not line:
            break
        decoded_line = line.decode(errors='replace').rstrip()

        # Активация логирования после второго обнаружения триггерной строки
        if trigger_str in decoded_line:
            trigger_count += 1
            if trigger_count == 2:
                logging_enabled = True
                log_file.write(f"[{datetime.now().isoformat()} {stream_type}] === НАЧАЛО ЛОГИРОВАНИЯ ===\n")
            continue

        if logging_enabled:
            log_entry = f"[{datetime.now().isoformat()} {stream_type}] {decoded_line}\n"
            log_file.write(log_entry)
            print(decoded_line)


def main():
    timeout = 300  
    script_dir = get_script_dir()
    log_path = os.path.join(script_dir, LOG_FILE)

    try:
        # Переход в целевую рабочую директорию
        target_path = os.path.abspath(os.path.join(script_dir, TARGET_DIR))
        os.chdir(target_path)
    except Exception as e:
        error_msg = f"Ошибка перехода в директорию {target_path}: {str(e)}"
        print(error_msg)
        with open(log_path, "a") as f:
            f.write(f"[ERROR] {datetime.now().isoformat()} {error_msg}\n")
        sys.exit(1)

    print(f"Лог-файл: {log_path}\nРабочая директория: {os.getcwd()}")

    try:
        with open(log_path, "a", buffering=1) as log_file:
            # Запись заголовка запуска
            log_file.write(f"\n{'='*50}\nНовый запуск {datetime.now().isoformat()}\n{'='*50}\n")
            
            # Запуск целевого процесса
            proc = subprocess.Popen(
                COMMAND,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Создание потоков для чтения выводов
            stdout_thread = threading.Thread(
                target=read_stream,
                args=(proc.stdout, "STDOUT", log_file, START_LOGGING_STR)
            )
            stderr_thread = threading.Thread(
                target=read_stream,
                args=(proc.stderr, "STDERR", log_file, START_LOGGING_STR)
            )
            
            # Старт потоков
            stdout_thread.start()
            stderr_thread.start()

            # Ожидание завершения процесса с таймаутом
            try:
                proc.wait(timeout=timeout)
            except TimeoutExpired:
                log_file.write(f"[TIMEOUT] {datetime.now().isoformat()} Таймаут 5 минут\n")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except TimeoutExpired:
                    log_file.write(f"[FORCE KILL] {datetime.now().isoformat()}\n")
                    proc.kill()
                    proc.wait()

            # Завершение потоков
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)

    except KeyboardInterrupt:
        with open(log_path, "a") as f:
            f.write(f"[INTERRUPTED] {datetime.now().isoformat()} Пользователь прервал выполнение\n")
        print("\nПрерывание пользователем")
        sys.exit(1)
    except Exception as e:
        with open(log_path, "a") as f:
            f.write(f"[CRITICAL] {datetime.now().isoformat()} {str(e)}\n")
        print(f"Критическая ошибка: {str(e)}")
        sys.exit(1)

    # Запись финального статуса
    exit_code = proc.returncode
    status = "УСПЕШНО" if exit_code == 0 else f"ОШИБКА ({exit_code})"
    with open(log_path, "a") as f:
        f.write(f"[FINISHED] {datetime.now().isoformat()} Завершено со статусом: {status}\n")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
