
from triage import triage_ticket

# Test tickets with their expected categories
test_cases = [
    {
        "ticket": "I paid for my course, but my batch is not visible.",
        "expected": "Course Access Issue"
    },
    {
        "ticket": "I want a refund for my payment.",
        "expected": "Payment Issue"
    },
    {
        "ticket": "I forgot my password and cannot log in.",
        "expected": "Account Issue"
    },
    {
        "ticket": "I paid twice and need my money back.",
        "expected": "Payment Issue"
    },
    {
        "ticket": "Please help me reset my password.",
        "expected": "Account Issue"
    },
    {
        "ticket": "My certificate has not arrived.",
        "expected": "Academic Support"
    },
    {
        "ticket": "My assignment submission is not working.",
        "expected": "Academic Support"
    },
    {
        "ticket": "I have a question about the course.",
        "expected": "General Inquiry"
    }
]

correct = 0

print("\nSTUDENT SUPPORT COPILOT - EVALUATION")
print("=" * 50)

for index, case in enumerate(test_cases, start=1):
    result = triage_ticket(case["ticket"])

    expected = case["expected"]
    predicted = result["category"]
    passed = predicted == expected

    if passed:
        correct += 1

    print(f"\nTest {index}: {'PASS' if passed else 'FAIL'}")
    print("Ticket:", case["ticket"])
    print("Expected:", expected)
    print("Predicted:", predicted)

accuracy = (correct / len(test_cases)) * 100

print("\n" + "=" * 50)
print(f"Tests passed: {correct}/{len(test_cases)}")
print(f"Classification accuracy: {accuracy:.2f}%")