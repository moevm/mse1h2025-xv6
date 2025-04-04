#!/bin/bash

VALID_LABS=("util" "syscall" "pgtbl" "traps" "cow" "net" "lock" "fs" "mmap")
BASE_DIR=$(realpath "$(dirname "$0")/..") 
LOGS_DIR="$BASE_DIR/logs"
SOLUTION_DIR="$BASE_DIR/solution"
RESULTS_DIR="$LOGS_DIR"
SCRIPTS_DIR="$BASE_DIR/scripts" 

if [[ $# -lt 1 ]]; then
    echo "Error: Parameters are not specified. Use --help for reference."
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
    echo "PURPOSE:"
    echo "  [1] _the_name_of_the_lab_"
    echo "  [2] _the_name_of_the_uploaded_archive_"
    echo " "
    echo "List of laboratory work names:"
    echo "  ${VALID_LABS[*]}"
    echo " "
    echo "Valid archive format:"
    echo " .zip, .tar, .gz, .tgz, .tar.gz, .7z, .rar"
    echo " "
    echo "The archive must contain the entire contents of the folder \"xv6-labs-2024/\" – the folder of the cloned (\"git clone git://g.csail.mit.edu/xv6-labs-2024\") for performing laboratory work of the repository, with the completed laboratory work (all necessary added files in the folder \"xv6-labs-2024/user/\")."
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

check_archive_exists() {
    local archive=$1
    if [[ ! -f "$archive" ]]; then
        echo "Error: Archive '$archive' not found."
        exit 1
    fi
}

prepare_grade_script() {
    local lab=$1
    file=$(find ./lab_ready -type f -name "grade-lab-*${lab}*" -print -quit)
    if [[ -z "$file" ]]; then
        echo "Error: No grading script found for lab $lab." | tee -a "$LOGS_DIR/error.log"
        python3 "$SCRIPTS_DIR/generate_report.py" "$archive_name"
        exit 1
    fi
    chmod +x "$file"
}

load_and_test_solution() {
    local lab=$1
    local archive=$2
    local archive_name=$(basename "$archive")
    local log_file="$LOGS_DIR/$archive_name.log"
    local report_file="$LOGS_DIR/$archive_name.json"

    # Создание дирректории с log-файлами и очистка старых логов в случае, если они уже существовали
    mkdir -p "$LOGS_DIR"
    rm -f "$LOGS_DIR/load.log" "$LOGS_DIR/file_checker.log" "$LOGS_DIR/qemu-gdb.log" "$LOGS_DIR/error.log"

    # load.py
    echo "Uploading the solution..."
    python3 "$SCRIPTS_DIR/load.py" "$archive"
    if [[ $? -ne 0 ]]; then
        echo "Error loading the solution. Details in the log: $log_file" | tee -a "$LOGS_DIR/error.log"
        python3 "$SCRIPTS_DIR/generate_report.py" "$archive_name"
        exit 1
    fi
    echo "The file has been uploaded successfully!"

    # file_checker.py
    echo "Checking the solution..."
    prepare_grade_script "$lab"
    python3 "$SCRIPTS_DIR/file_checker.py"
    if [[ $? -ne 0 ]]; then
        echo "Error: file_checker failed. See $log_file for details." | tee -a "$LOGS_DIR/error.log"
        python3 "$SCRIPTS_DIR/generate_report.py" "$archive_name"
        exit 1
    fi

    # run_tests.py
    python3 "$SCRIPTS_DIR/run_tests.py"
    if [[ $? -ne 0 ]]; then
        echo "Error: run_tests failed. See $log_file for details." | tee -a "$LOGS_DIR/error.log"
        python3 "$SCRIPTS_DIR/generate_report.py" "$archive_name"
        exit 1
    fi

    # generate_report.py
    python3 "$SCRIPTS_DIR/generate_report.py"
    if [[ $? -ne 0 ]]; then
        echo "Error: generate_report failed. See $log_file for details." | tee -a "$log_file"
        exit 1
    fi
    echo "The results of the check are saved to a file \"$report_file\"."
}

show_report() {
    local lab=$1
    local archive=$2
    local archive_name=$(basename "$archive")
    local report_file="$LOGS_DIR/$archive_name.log"

    if [[ ! -f "$report_file" ]]; then
        echo "Error: The report file $report_file not found."
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
            echo "Error: Incorrect parameters are specified. Use --help for reference."
            exit 1
        fi
        is_valid_lab "$2" || { echo "Error: A non-existent laboratory work is indicated"; exit 1; }
        check_archive_exists "$3"
        load_and_test_solution "$2" "$3"
        ;;
    --report)
        if [[ $# -ne 3 ]]; then
            echo "Error: Incorrect parameters are specified. Use --help for reference."
            exit 1
        fi
        is_valid_lab "$2" || { echo "Error: A non-existent laboratory work is indicated"; exit 1; }
        check_archive_exists "$3"
        show_report "$2" "$3"
        ;;
    *)
        echo "Error: Unknown flag '$1'. Use --help for reference."
        exit 1
        ;;
esac
