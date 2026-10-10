
from triage import triage_ticket

# 36 labeled test tickets for the rule-based classifier
test_cases = [
    # Course Access Issue (7)
    {"ticket": "I paid for my course, but my batch is not visible.", "expected": "Course Access Issue"},
    {"ticket": "I cannot access my course materials.", "expected": "Course Access Issue"},
    {"ticket": "I can't open my lessons.", "expected": "Course Access Issue"},
    {"ticket": "My enrollment is missing.", "expected": "Course Access Issue"},
    {"ticket": "The batch not visible on my dashboard.", "expected": "Course Access Issue"},
    {"ticket": "I cannot access the course after registering.", "expected": "Course Access Issue"},
    {"ticket": "My course materials are not available.", "expected": "Course Access Issue"},

    # Payment Issue (7)
    {"ticket": "I want a refund for my payment.", "expected": "Payment Issue"},
    {"ticket": "My payment failed.", "expected": "Payment Issue"},
    {"ticket": "I paid twice for the same course.", "expected": "Payment Issue"},
    {"ticket": "My transaction is still pending.", "expected": "Payment Issue"},
    {"ticket": "I was charged twice for my order.", "expected": "Payment Issue"},
    {"ticket": "Money was deducted from my account.", "expected": "Payment Issue"},
    {"ticket": "I have a question about my billing.", "expected": "Payment Issue"},

    # Account Issue (7)
    {"ticket": "I forgot my password.", "expected": "Account Issue"},
    {"ticket": "I cannot login to my account.", "expected": "Account Issue"},
    {"ticket": "Please help me reset my password.", "expected": "Account Issue"},
    {"ticket": "I cannot log in to the portal.", "expected": "Account Issue"},
    {"ticket": "I need to update my registered email.", "expected": "Account Issue"},
    {"ticket": "How can I change my email address?", "expected": "Account Issue"},
    {"ticket": "I have a problem with my account.", "expected": "Account Issue"},

    # Academic Support (8)
    {"ticket": "My certificate has not arrived.", "expected": "Academic Support"},
    {"ticket": "My assignment submission is not working.", "expected": "Academic Support"},
    {"ticket": "Please explain this mathematics concept.", "expected": "Academic Support"},
    {"ticket": "I need help with my quiz.", "expected": "Academic Support"},
    {"ticket": "My grades are incorrect.", "expected": "Academic Support"},
    {"ticket": "I need help with my coursework.", "expected": "Academic Support"},
    {"ticket": "Please provide some practice questions.", "expected": "Academic Support"},
    {"ticket": "My exam starts in 10 minutes and I cannot access exam.", "expected": "Academic Support"},

    # General Inquiry (7)
    {"ticket": "What are your support hours?", "expected": "General Inquiry"},
    {"ticket": "Where can I find the campus address?", "expected": "General Inquiry"},
    {"ticket": "Please tell me about the platform.", "expected": "General Inquiry"},
    {"ticket": "Thank you for your help.", "expected": "General Inquiry"},
    {"ticket": "I have a general question.", "expected": "General Inquiry"},
    {"ticket": "Can you explain the available services?", "expected": "General Inquiry"},
    {"ticket": "Where can I find more information?", "expected": "General Inquiry"},
]


def main():
    correct = 0
    failures = []
    category_totals = {}

    print("\nSTUDENT SUPPORT COPILOT - CLASSIFICATION EVALUATION")
    print("=" * 60)

    for index, case in enumerate(test_cases, start=1):
        result = triage_ticket(case["ticket"])
        expected = case["expected"]
        predicted = result["category"]
        passed = predicted == expected

        category_totals.setdefault(expected, {"correct": 0, "total": 0})
        category_totals[expected]["total"] += 1

        if passed:
            correct += 1
            category_totals[expected]["correct"] += 1
        else:
            failures.append({
                "number": index,
                "ticket": case["ticket"],
                "expected": expected,
                "predicted": predicted,
            })

        print(
            f"Test {index:02}: {'PASS' if passed else 'FAIL'} | "
            f"Expected: {expected} | Predicted: {predicted}"
        )

    total = len(test_cases)
    accuracy = correct / total * 100

    print("\n" + "=" * 60)
    print(f"Tests passed: {correct}/{total}")
    print(f"Tests failed: {total - correct}/{total}")
    print(f"Classification accuracy: {accuracy:.2f}%")

    print("\nCATEGORY-WISE RESULTS")
    for category, stats in category_totals.items():
        score = stats["correct"] / stats["total"] * 100
        print(
            f"{category}: {stats['correct']}/{stats['total']} "
            f"({score:.2f}%)"
        )

    if failures:
        print("\nFAILED CASES")
        for failure in failures:
            print(f"\nTest {failure['number']}: {failure['ticket']}")
            print(f"Expected:  {failure['expected']}")
            print(f"Predicted: {failure['predicted']}")

    print("\nNote: Results measure this rule-based test set only.")


if __name__ == "__main__":
    main()