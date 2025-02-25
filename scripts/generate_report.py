import json

def analyze_log(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            logs = file.read()
            if "FAILED" in logs:
                return {"status": "FAIL", "score": 0}
            elif "PASSED" in logs:
                return {"status": "PASS", "score": 100}
            else:
                return {"status": "UNKNOWN", "score": 0}
    except FileNotFoundError:
        return {"status": "ERROR", "score": 0, "message": "test.log not found"}

def save_result(data, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

result = analyze_log("test.log")
save_result(result, "result.json")
