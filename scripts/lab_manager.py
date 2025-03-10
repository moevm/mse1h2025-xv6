import sys
import subprocess


def main():
    solution_loaded = False
    solution_checked = False
    tests_run = False

    while True:
        print("\nМеню:")
        print("1. Загрузить решение")
        print("2. Проверить решение")
        print("3. Показать результаты проверки")
        print("4. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            solution_loaded = load_solution()
        elif choice == "2":
            if not solution_loaded:
                print("Ошибка: Сначала загрузите решение!")
            else:
                solution_checked = check_solution()
        elif choice == "3":
            if not solution_checked:
                print("Ошибка: Сначала проверьте решение!")
            else:
                tests_run = run_tests()
                if tests_run:
                    show_results()
        elif choice == "4":
            print("Выход из программы...")
            sys.exit()
        else:
            print("Ошибка: Неверный ввод, попробуйте снова.")


def load_solution():
    print("Загрузка решения...")
    result = subprocess.run([sys.executable, "upload_solution.py"], capture_output=True, text=True, encoding="utf-8")
    print(result.stdout)

    if result.returncode != 0:
        print("Ошибка при загрузке решения!")
        print(result.stderr)
    return result.returncode == 0


def check_solution():
    result = subprocess.run([sys.executable, "file_checker.py"], capture_output=True, text=True, encoding="utf-8")

    if result.returncode != 0:
        print("Ошибка при проверке файлов!")
        print(result.stderr)
        return False
    print("Файлы успешно проверены.")
    return True


def run_tests():
    print("Проверка решения началась...")
    result = subprocess.run([sys.executable, "run_tests.py"], capture_output=True, text=True, encoding="utf-8")

    if "FAILED" in result.stdout:
        print("Тесты не пройдены.")
        print(result.stdout)
        return False
    elif "PASSED" in result.stdout:
        print("Тесты успешно пройдены.")
        return True
    else:
        print("Неизвестная ошибка при запуске тестов.")
        print(result.stdout)
        return False


def show_results():
    print("Генерация результатов проверки...")
    subprocess.run([sys.executable, "generate_report.py"], capture_output=True, text=True, encoding="utf-8")

    try:
        with open("result.json", "r", encoding="utf-8") as file:
            print(file.read())
    except FileNotFoundError:
        print("Ошибка: Файл result.json не найден.")


if __name__ == "__main__":
    main()
