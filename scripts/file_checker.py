import os

def check_encoding(file_path): 
    try: 
        with open(file_path, 'r', encoding='utf-8-sig') as f: 
            f.read()
        return True, "" 
    except UnicodeDecodeError: 
        return False, f"Ошибка: файл '{file_path}' не в кодировке 'utf-8'."


def check_size(file_path, max_size_mb=1):
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # размер в мб

    if file_size > max_size_mb:
        return False, f"Ошибка: файл '{file_path}' превышает максимальный размер {max_size_mb} мб."
    return True, ""


def check_extension(file_path, valid_extensions):
    _, ext = os.path.splitext(file_path)
    if ext not in valid_extensions:
        return False, f"Ошибка: файл '{file_path}' имеет недопустимое расширение '{ext}'. Ожидаются: {', '.join(valid_extensions)}."
    return True, ""


def validate_files(directory, valid_extensions, max_size_mb=10):
    errors = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):

            is_valid_encoding, encoding_error = check_encoding(file_path)
            if not is_valid_encoding:
                errors.append(encoding_error)

            is_valid_size, size_error = check_size(file_path, max_size_mb)
            if not is_valid_size:
                errors.append(size_error)

            is_valid_extension, extension_error = check_extension(file_path, valid_extensions)
            if not is_valid_extension:
                errors.append(extension_error)

    return errors

if __name__ == "__main__":
    directory_to_check = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'solution')
    valid_extensions = ['.c', '.h', '.txt']
    errors = validate_files(directory_to_check, valid_extensions)

    if errors:
        for error in errors:
            print(error)
    else:
        print("Все файлы соответствуют требованиям.")
