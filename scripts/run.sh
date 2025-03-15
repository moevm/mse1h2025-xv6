#!/bin/bash

VALID_LABS=("util" "syscall" "pgtbl" "traps" "cow" "net" "lock" "fs" "mmap")
BASE_DIR=$(realpath "$(dirname "$0")")  
LOGS_DIR="$BASE_DIR/logs"
SOLUTION_DIR="$BASE_DIR/solution"
RESULTS_DIR="$LOGS_DIR"

if [[ $# -lt 1 ]]; then
    echo "Ошибка: Не указаны параметры. Используйте --help для справки."
    exit 1
fi

show_help() {
    echo "=================================================="
    echo "            Автоматизированная система   "
    echo "            проверки решений Lab 6.828   "
    echo "=================================================="
    echo "Использование: ./run.sh [КЛЮЧ]... [ЦЕЛЬ]..."
    echo "Ключи (флаги):"
    echo "  --help             Вывод этой инструкции"
    echo "  --load [LAB] [ARCHIVE]  Загрузить решение"
    echo "  --test [LAB] [ARCHIVE]      Проверить решение"
    echo "  --report [LAB] [ARCHIVE]    Показать результаты проверки"
    echo "Цели:"
    echo "  [LAB] - название лабораторной работы"
    echo "  [ARCHIVE] - название загруженного архива"
    echo "Список названий лабораторных работ:"
    echo "  ${VALID_LABS[*]}"
    echo "=================================================="
    exit 0
}

is_valid_lab() {
    local lab=$1
    for valid_lab in "${VALID_LABS[@]}"; do
        if [[ "$lab" == "$valid_lab" ]]; then
            return 0
        fi
    done
    return 1
}

is_valid_archive() {
    local archive=$1
    if [[ "$archive" =~ \.(zip|rar|7z|tar)$ ]]; then
        return 0
    else
        return 1
    fi
}

check_archive_exists() {
    local archive=$1
    if [[ ! -f "$BASE_DIR/$archive" ]]; then
        echo "Ошибка: Архив '$archive' не найден в $BASE_DIR."
        exit 1
    fi
}

load_solution() {
    local lab=$1
    local archive=$2
    local log_file="$LOGS_DIR/$lab/$archive.log"

    is_valid_archive "$archive" || { echo "Ошибка: Архив $archive должен быть в формате .zip, .rar, .7z или .tar"; exit 1; }

    mkdir -p "$LOGS_DIR/$lab"
    echo "Загрузка решения..." | tee "$log_file"
    python3 "$BASE_DIR/load.py" "$BASE_DIR/$archive" >> "$log_file" 2>&1
    if [[ $? -ne 0 ]]; then
        echo "Ошибка при загрузке решения. Подробности в логе: $log_file"
        exit 1
    fi

    echo "Файл успешно загружен!" | tee -a "$log_file"
}

test_solution() {
    local lab=$1
    local archive=$2
    local log_file="$LOGS_DIR/$lab/$archive.log"
    local report_file="result.json"

    if [[ ! -f "$log_file" ]]; then
        echo "Ошибка: Решение не было загружено. Сначала выполните --load."
        exit 1
    fi

    echo "Выполнение тривиальных проверок..." | tee -a "$log_file"
    python3 "$BASE_DIR/file_checker.py" >> "$log_file" 2>&1
    if [[ $? -ne 0 ]]; then
        echo "Ошибка: Файл не прошел тривиальные проверки. Подробности в логе: $log_file"
        exit 1
    fi

    echo "Проверка решения..." | tee -a "$log_file"
    python3 "$BASE_DIR/run_tests.py" >> "$log_file" 2>&1
    if [[ -f "$BASE_DIR/test.log" ]]; then
        cat "$BASE_DIR/test.log" >> "$log_file"
    fi
    if [[ $? -ne 0 ]]; then
        echo "Ошибка: Не удалось запустить тесты. Подробности в логе: $log_file"
        exit 1
    fi

    echo "Генерация отчета..." | tee -a "$log_file"
    python3 "$BASE_DIR/generate_report.py" >> "$log_file" 2>&1
    if [[ $? -ne 0 ]]; then
        echo "Ошибка: Не удалось сгенерировать отчет. Подробности в логе: $log_file"
        exit 1
    fi
    printf "0r %s\nw\n" "$log_file" | ed -s "$report_file" >/dev/null 2>&1
    echo "Результаты проверки сохранены в файл $log_file" | tee -a "$log_file"
}

show_report() {
    local report_file="result.json"

    if [[ ! -f "$report_file" ]]; then
        echo "Ошибка: Файл отчета $report_file не найден."
        exit 1
    fi

    echo "Содержимое result.json:"
    cat "$report_file"
    
}



case "$1" in
    --help)
        show_help
        ;;
    --load)
        if [[ $# -ne 3 ]]; then
            echo "Ошибка: Указаны неверные параметры. Используйте --help для справки."
            exit 1
        fi
        is_valid_lab "$2" || { echo "Ошибка: Указана несуществующая лабораторная работа"; exit 1; }
        check_archive_exists "$3"
        load_solution "$2" "$3"
        ;;
    --test)
        if [[ $# -ne 3 ]]; then
            echo "Ошибка: Указаны неверные параметры. Используйте --help для справки."
            exit 1
        fi
        is_valid_lab "$2" || { echo "Ошибка: Указана несуществующая лабораторная работа"; exit 1; }
        check_archive_exists "$3"
        test_solution "$2" "$3"
        ;;
    --report)
        if [[ $# -ne 3 ]]; then
            echo "Ошибка: Указаны неверные параметры. Используйте --help для справки."
            exit 1
        fi
        is_valid_lab "$2" || { echo "Ошибка: Указана несуществующая лабораторная работа"; exit 1; }
        check_archive_exists "$3"
        show_report "$2" "$3"
        ;;
    *)
        echo "Ошибка: Неизвестный флаг '$1'. Используйте --help для справки."
        exit 1
        ;;
esac
