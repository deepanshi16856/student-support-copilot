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

category_passed = 0
priority_passed = 0

print("\n===== RULE-BASED EVALUATION =====\n")

for i, case in enumerate(test_cases, start=1):
    ticket, expected_category, expected_priority = case


    result = triage_ticket(ticket)

    category_ok = result["category"] == expected_category
    priority_ok = result["priority"] == expected_priority

    if category_ok:
        category_passed += 1

    if priority_ok:
        priority_passed += 1

    status = "PASS" if category_ok and priority_ok else "FAIL"

    print(f"Test {i}: {status}")
    print(f"Ticket: {ticket}")
    print(f"Category: {result['category']} | Expected: {expected_category}")
    print(f"Priority: {result['priority']} | Expected: {expected_priority}")
    print("-" * 50)

total = len(test_cases)

print("\n===== EVALUATION SUMMARY =====")
print(f"Total test cases: {total}")
print(f"Category tests passed: {category_passed}/{total} ({category_passed / total * 100:.1f}%)")
print(f"Priority tests passed: {priority_passed}/{total} ({priority_passed / total * 100:.1f}%)")
print(f"Overall checks passed: {category_passed + priority_passed}/{total * 2} ({(category_passed + priority_passed) / (total * 2) * 100:.1f}%)")
