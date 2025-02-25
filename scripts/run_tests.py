import subprocess
import sys

def main():
    timeout = 30  
    solution_script = 'solution/solution.py'  
    log_file_name = 'test.log'
    status = "FAILED"

    try:
        result = subprocess.run(
            [sys.executable, solution_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            text=True,
            encoding='utf-8'
        )
        
        with open(log_file_name, 'w') as log_file:
            log_file.write(result.stdout)
       
        status = "PASSED" if result.returncode == 0 else "FAILED"
    
    except subprocess.TimeoutExpired as e:
        with open(log_file_name, 'w') as log_file:
            log_file.write(e.stdout or "")
            log_file.write(f"\nОшибка: Превышено время выполнения ({timeout} сек.)\n")
        status = "FAILED"
    except FileNotFoundError:
        with open(log_file_name, 'w') as log_file:
            log_file.write(f"Ошибка: Файл {solution_script} не найден\n")
        status = "FAILED"
    except Exception as e:
        with open(log_file_name, 'w') as log_file:
            log_file.write(f"Неизвестная ошибка: {str(e)}\n")
        status = "FAILED"
    print(status)

if __name__ == "__main__":
    main()