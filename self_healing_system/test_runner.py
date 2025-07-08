# Real Test Runner Integration (Pytest example)
import subprocess

def rerun_test(test_id):
    # Example: run pytest for a specific test
    result = subprocess.run(["pytest", f"tests/{test_id}.py"], capture_output=True, text=True)
    return "pass" if result.returncode == 0 else "fail"
