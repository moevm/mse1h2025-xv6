import os
import sys
import logging
from datetime import datetime

def setup_logger(logs_dir):
    os.makedirs(logs_dir, exist_ok=True)  #создание папки для логов, если её нет

    log_filename = "file_checker.log"  #название файла лога
    log_path = os.path.join(logs_dir, log_filename)  #путь к файлу лога

    logger = logging.getLogger('FileChecker')  #создание логгера
    logger.setLevel(logging.INFO)  #уровень логирования - INFO

    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')  #обработчик для записи в файл
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))  #формат лога

    stream_handler = logging.StreamHandler(sys.stdout)  #обработчик для вывода в консоль
    stream_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))  #формат для консоли

    logger.addHandler(file_handler)  #добавляем обработчик в логгер
    # logger.addHandler(stream_handler)  #добавляем обработчик для консоли # It is just superfluous

    logger.info(f"Logging started. Logs are saved to: {log_path}")  #сообщение о запуске логирования

    return logger

def check_encoding(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:  #открытие файла с указанной кодировкой
            f.read()
        return True, ""
    except UnicodeDecodeError:  #если не удалось прочитать в нужной кодировке
        return False, f"Error: file '{file_path}' is not in 'utf-8' encoding."

def check_size(file_path, max_size_mb=1):
    file_size = os.path.getsize(file_path) / (1024 * 1024)  #получение размера файла в МБ
    if file_size > max_size_mb:  #если размер файла превышает допустимый
        return False, f"Error: file '{file_path}' exceeds the maximum size of {max_size_mb} MB."
    return True, ""

def check_extension(file_path, valid_extensions):
    _, ext = os.path.splitext(file_path)  #получаем расширение файла
    if ext not in valid_extensions:  #если расширение не подходит
        return False, f"Error: file '{file_path}' has an invalid extension '{ext}'. Expected: {', '.join(valid_extensions)}."
    return True, ""

def validate_files(lab_ready_path, valid_extensions, logger, max_size_mb=10):
    errors = []
    user_dirs_checked = 0
    files_checked = 0

    for dirpath, dirnames, filenames in os.walk(lab_ready_path):
        if os.path.basename(dirpath) == 'user':
            user_dirs_checked += 1
            logger.info(f"\nChecking folder: {dirpath}")

            for filename in filenames:
                files_checked += 1
                file_path = os.path.join(dirpath, filename)
                logger.info(f"Checking file: {file_path}")

                is_valid_encoding, encoding_error = check_encoding(file_path)
                if not is_valid_encoding:
                    logger.error(encoding_error)
                    errors.append(encoding_error)

                is_valid_size, size_error = check_size(file_path, max_size_mb)
                if not is_valid_size:
                    logger.error(size_error)
                    errors.append(size_error)

                is_valid_extension, extension_error = check_extension(file_path, valid_extensions)
                if not is_valid_extension:
                    logger.error(extension_error)
                    errors.append(extension_error)

    return errors, user_dirs_checked, files_checked

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))  #определение базовой директории проекта

    #папки lab_ready и logs находятся на одном уровне с скриптом
    lab_ready_path = os.path.join(base_dir, 'lab_ready')
    logs_dir = os.path.join(base_dir, 'logs')

    #проверка существования папки lab_ready
    if not os.path.exists(lab_ready_path):
        print(f"Folder lab_ready not found at path: {lab_ready_path}")
        sys.exit(1)

    logger = setup_logger(logs_dir)  #настройка логгера

    logger.info(f"Starting file check in 'user' folders within: {lab_ready_path}")

    valid_extensions = ['.c', '.h', '.txt', '.py', '.S', '.ld', '.pl', '.sh']  #разрешённые расширения файлов

    errors, user_dirs_checked, files_checked = validate_files(lab_ready_path, valid_extensions, logger)

    # логируем summary
    logger.info(f"Summary: checked {user_dirs_checked} 'user' folders, {files_checked} files, found {len(errors)} error(s).")

    if errors:
        logger.warning("\nErrors found during file check:\n")
        for error in errors:
            logger.warning(error)
        logger.info("File check completed with errors.")
        sys.exit(1)
    else:
        logger.info("All files meet the requirements!")

