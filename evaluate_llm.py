import time
from llm_triage import triage_ticket_with_llm

test_cases = [
    {
        "ticket": "I paid for my course, but my batch is not visible.",
        "expected_category": "Course Access Issue",
        "expected_priority": "High"
    },
    {
        "ticket": "My payment failed, but money was deducted.",
        "expected_category": "Payment Issue",
        "expected_priority": "High"
    },
    {
        "ticket": "I forgot my password and cannot log in.",
        "expected_category": "Account Issue",
        "expected_priority": "Medium"
    },
    {
        "ticket": "I cannot submit my assignment.",
        "expected_category": "Academic Support",
        "expected_priority": "Medium"
    },
    {
        "ticket": "I want to know more about your courses.",
        "expected_category": "General Inquiry",
        "expected_priority": "Low"
    }
]

category_correct = 0
priority_correct = 0
completed = 0

print("\n===== Gemini LLM Evaluation =====")

for index, case in enumerate(test_cases, start=1):
    print(f"\nTest Case {index}: {case['ticket']}")

    try:
        result = triage_ticket_with_llm(case["ticket"])

        category_pass = (
            result["category"] == case["expected_category"]
        )
        priority_pass = (
            result["priority"] == case["expected_priority"]
        )

        completed += 1
        category_correct += category_pass
        priority_correct += priority_pass

        print("Predicted category:", result["category"])
        print("Expected category:", case["expected_category"])
        print("Category:", "PASS" if category_pass else "FAIL")

        print("Predicted priority:", result["priority"])
        print("Expected priority:", case["expected_priority"])
        print("Priority:", "PASS" if priority_pass else "FAIL")

    except Exception as error:
        print("Test could not be completed:", error)
        time.sleep(3)

if completed:
    category_accuracy = category_correct / completed * 100
    priority_accuracy = priority_correct / completed * 100

    print("\n===== Evaluation Summary =====")
    print(f"Completed tests: {completed}/{len(test_cases)}")
    print(f"Category accuracy: {category_accuracy:.1f}%")
    print(f"Priority accuracy: {priority_accuracy:.1f}%")
else:
    print("\nNo tests completed successfully.")
    print("Check Gemini availability and try again.")