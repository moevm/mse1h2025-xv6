## Результаты тестирования
Все тесты успешно пройдены

### Статус тестов
| Категория тестов          | Статус     |
|---------------------------|------------|
| Загрузка файлов           | ✔️ Успешно |
| Разархивирование          | ✔️ Успешно |
| Применение патчей         | ✔️ Успешно |
| Логирование               | ✔️ Успешно |
| Обработка таймаутов       | ✔️ Успешно |
| Тесты меню                | ✔️ Успешно |

## Выполнение тестов

### Разархивирование
![test_downloader.png](https://github.com/moevm/mse1h2025-xv6/blob/37-Launching-Unit-Tests/tests/pictures/test_downloader.png)

### Загрузка файлов, проверка логов
![test_integration.png](https://github.com/moevm/mse1h2025-xv6/blob/37-Launching-Unit-Tests/tests/pictures/test_integration.png)


### Запуск лабораторных
![test_lab_runner.png](https://github.com/moevm/mse1h2025-xv6/blob/37-Launching-Unit-Tests/tests/pictures/test_lab_runner.png)

### Применение патчей
![test_patcher.png](https://github.com/moevm/mse1h2025-xv6/blob/37-Launching-Unit-Tests/tests/pictures/test_patcher.png)

### Тесты меню
![test_menu_interface.png](https://github.com/moevm/mse1h2025-xv6/blob/37-Launching-Unit-Tests/tests/pictures/test_menu_interface.png)

## Логи выполнения тестов
```text
test_downloader.py
C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe "C:/Program Files/JetBrains/PyCharm Community Edition 2023.3.2/plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py" --path C:\Users\Admin\Downloads\try\tests\test_downloader.py 
Testing started at 0:41 ...
Launching pytest with arguments C:\Users\Admin\Downloads\try\tests\test_downloader.py --no-header --no-summary -q in C:\Users\Admin\Downloads\try\tests

============================= test session starts =============================
collecting ... collected 3 items

test_downloader.py::TestDownloader::test_empty_archive PASSED            [ 33%]
test_downloader.py::TestDownloader::test_extract_valid_archive PASSED    [ 66%]
test_downloader.py::TestDownloader::test_invalid_archive_format PASSED   [100%]

============================== 3 passed in 0.11s ==============================

Process finished with exit code 0

test_integration.py
C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe "C:/Program Files/JetBrains/PyCharm Community Edition 2023.3.2/plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py" --path C:\Users\Admin\Downloads\try\tests\test_integration.py 
Testing started at 0:41 ...
Launching pytest with arguments C:\Users\Admin\Downloads\try\tests\test_integration.py --no-header --no-summary -q in C:\Users\Admin\Downloads\try\tests

============================= test session starts =============================
collecting ... collected 3 items

test_integration.py::test_integration PASSED                             [ 33%]
Using patch from: C:\Program Files\Git\usr\bin\patch.EXE
Script path: C:\Users\Admin\Downloads\try\scripts\load.py

test_integration.py::test_error_handling PASSED                          [ 66%]
test_integration.py::test_no_patch_scenario PASSED                       [100%]

============================== 3 passed in 0.67s ==============================

Process finished with exit code 0

test_lab_runner.py
PASSED      [100%]Makefile not found C:\Users\Admin\Downloads\try\lab_ready
Лог-файл: C:\Users\Admin\Downloads\try\logs\qemu-gdb.log
Working directory: C:\Users\Admin\Downloads\try\tests

test_menu_interface.py
C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe "C:/Program Files/JetBrains/PyCharm Community Edition 2023.3.2/plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py" --path C:\Users\Admin\Downloads\try\tests\test_menu_interface.py 
Testing started at 0:43 ...
Launching pytest with arguments C:\Users\Admin\Downloads\try\tests\test_menu_interface.py --no-header --no-summary -q in C:\Users\Admin\Downloads\try\tests

============================= test session starts =============================
collecting ... collected 1 item

test_menu_interface.py::test_menu_interface PASSED                       [100%]

============================== 1 passed in 0.18s ==============================

Process finished with exit code 0

test_patcher.py
C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe "C:/Program Files/JetBrains/PyCharm Community Edition 2023.3.2/plugins/python-ce/helpers/pycharm/_jb_pytest_runner.py" --path C:\Users\Admin\Downloads\try\tests\test_patcher.py 
Testing started at 0:43 ...
Launching pytest with arguments C:\Users\Admin\Downloads\try\tests\test_patcher.py --no-header --no-summary -q in C:\Users\Admin\Downloads\try\tests

============================= test session starts =============================
collecting ... collected 2 items

test_patcher.py::TestPatcher::test_apply_patch_success PASSED            [ 50%]
test_patcher.py::TestPatcher::test_patch_failure PASSED                  [100%]

============================== 2 passed in 0.15s ==============================

Process finished with exit code 0

