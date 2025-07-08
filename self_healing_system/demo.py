import requests

# Step 1: Add a failing test run
def add_failing_test_run():
    r = requests.post("http://127.0.0.1:5000/add_test_run", json={
        "test_id": "test1",
        "element_id": "elem42",
        "locator": "//button[@id='submit']",
        "result": "fail",
        "failure_reason": "Element not found"
    })
    print("Add test run:", r.json())

# Step 2: Automated healing and feedback
def auto_heal_and_feedback():
    r = requests.post("http://127.0.0.1:5000/auto_heal_and_feedback", json={
        "element_id": "elem42",
        "test_id": "test1",
        "locator": "//button[@id='submit']"
    })
    print("Auto heal and feedback:", r.json())

if __name__ == "__main__":
    add_failing_test_run()
    auto_heal_and_feedback()
