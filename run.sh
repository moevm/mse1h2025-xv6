#!/bin/bash

VALID_LABS=("util" "syscall" "pgtbl" "traps" "cow" "net" "lock" "fs" "mmap")
BASE_DIR=$(realpath "$(dirname "$0")/..") 
LOGS_DIR="$BASE_DIR/logs"
SOLUTION_DIR="$BASE_DIR/solution"
RESULTS_DIR="$LOGS_DIR"
SCRIPTS_DIR="$BASE_DIR/scripts" 

if [[ $# -lt 1 ]]; then
    echo "Ошибка: Не указаны параметры. Используйте --help для справки."
    exit 1
fi

show_help() {
    echo "=================================================="
    echo "                 Automated system"
    echo "            verification of Lab 6.828"
    echo "=================================================="
    echo "USE: ./run.sh [KEYS]... [TARGET]..."
    echo "KEYS (flags):"
    echo "  --help             The output of this instruction"
    echo "  --validate [1] [2] Download and verify the solution"
    echo "  --report [1] [2]   Show the verification results"
    echo "PURPUSE:"
    echo "  [1] _the_name_of_the_lab_"
    echo "  [2] _the_name_of_the_uploaded_archive_"
    echo "List of laboratory work names:"
    echo "  ${VALID_LABS[*]}"
    echo "=================================================="
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
    if [[ ! -f "$archive" ]]; then
        echo "Ошибка: Архив '$archive' не найден."
        exit 1
    fi
}

load_and_test_solution() {
    local lab=$1
    local archive=$2
    local archive_name=$(basename "$archive")
    local log_file="$LOGS_DIR/$archive_name.log"
    local report_file="$LOGS_DIR/$archive_name.json"

    mkdir -p "$LOGS_DIR"

    echo "Uploading the solution..."
    is_valid_archive "$archive" || { echo "Ошибка: Архив $archive должен быть в формате .zip, .rar, .7z или .tar"; exit 1; }

    python3 "$SCRIPTS_DIR/load.py" "$archive" >> "$log_file" 2>&1
    if [[ $? -ne 0 ]]; then
        echo "Ошибка при загрузке решения. Подробности в логе: $log_file"
        exit 1
    fi

    echo "The file has been uploaded successfully!"

    echo "Checking the solution..."
    echo "Trivial checks: " >> "$log_file"
    python3 "$SCRIPTS_DIR/file_checker.py" >> "$log_file" 2>&1
    python3 "$SCRIPTS_DIR/run_tests.py" >> "$log_file" 2>&1
    python3 "$SCRIPTS_DIR/generate_report.py" >> "$log_file" 2>&1

    if [[ -f "$BASE_DIR/test.log" ]]; then
        cat "$BASE_DIR/test.log" >> "$log_file"
    fi
    echo "Checking the performance of laboratory work: " >> "$log_file"
    echo "The results of the check are saved to a file \"$report_file\"."
}

show_report() {
    local lab=$1
    local archive=$2
    local archive_name=$(basename "$archive")
    local report_file="$LOGS_DIR/$archive_name.log"

    if [[ ! -f "$report_file" ]]; then
        echo "Ошибка: Файл отчета $report_file не найден."
        exit 1
    fi

    echo "Found the file \"$report_file\"."

    echo "Checking the archive format:"

    cat "$report_file"
}

case "$1" in
    --help)
        show_help
        ;;
    --validate)
        if [[ $# -ne 3 ]]; then
            echo "Ошибка: Указаны неверные параметры. Используйте --help для справки."
            exit 1
        fi
        is_valid_lab "$2" || { echo "Ошибка: Указана несуществующая лабораторная работа"; exit 1; }
        check_archive_exists "$3"
        load_and_test_solution "$2" "$3"
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
