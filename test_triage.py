
from triage import triage_ticket

test_cases = [
    ("I paid for my course, but my batch is not visible.", "Course Access Issue", "High"),
    ("My payment failed, but money was deducted.", "Payment Issue", "High"),
    ("I forgot my password and cannot log in.", "Account Issue", "Medium"),
    ("I cannot submit my assignment.", "Academic Support", "Medium"),
    ("I want to know more about your courses.", "General Inquiry", "Low"),
    ("Please refund the fee charged twice.", "Payment Issue", "High"),
    ("My account password reset is not working.", "Account Issue", "Medium"),
    ("The exam quiz page is not loading.", "Academic Support", "Medium"),
    ("I cannot access my course materials.", "Course Access Issue", "High"),
    ("Where can I find information about your platform?", "General Inquiry", "Low"),
    ("I paid yesterday and still cannot open my lessons.", "Course Access Issue", "High"),
    ("I need help changing my registered email address.", "Account Issue", "Medium"),
    ("The certificate for my completed course is missing.", "Academic Support", "Medium"),
    ("I was charged twice and need my money back urgently.", "Payment Issue", "High"),
    ("Hello, I have a question about your services.", "General Inquiry", "Low"),
]

category_correct = 0
priority_correct = 0

print("\n===== Rule-Based Evaluation =====")

for index, (ticket, expected_category, expected_priority) in enumerate(test_cases, start=1):
    result = triage_ticket(ticket)

    category_pass = result["category"] == expected_category
    priority_pass = result["priority"] == expected_priority

    category_correct += int(category_pass)
    priority_correct += int(priority_pass)

    print(f"\nTest {index}: {ticket}")
    print("Category:", "PASS" if category_pass else f"FAIL (got {result['category']})")
    print("Priority:", "PASS" if priority_pass else f"FAIL (got {result['priority']})")

print("\n===== Evaluation Summary =====")
print(f"Category accuracy: {category_correct / len(test_cases) * 100:.1f}%")
print(f"Priority accuracy: {priority_correct / len(test_cases) * 100:.1f}%")