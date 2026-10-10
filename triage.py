
def triage_ticket(ticket_text):
    text = ticket_text.lower()

    # Keywords for course access issues
    course_access_keywords = [
        "batch is not visible",
        "batch not visible",
        "course access",
        "cannot access",
        "can't access",
        "cannot open",
        "can't open",
        "lessons",
        "course materials",
        "not visible",
        "enrollment",
        "enrolment",
    ]

    # Keywords for payment issues
    payment_keywords = [
        "payment",
        "paid",
        "fee",
        "refund",
        "transaction",
        "charged",
        "money was deducted",
        "money back",
        "double charge",
        "charged twice",
        "billing",
    ]

    # Keywords for account issues
    account_keywords = [
        "password",
        "login",
        "log in",
        "account",
        "registered email",
        "email address",
        "change my email",
        "reset my email",
    ]

    # Keywords for urgent academic problems
    urgent_academic_keywords = [
        "exam starts in",
        "exam starting now",
        "exam is starting",
        "exam starts now",
        "exam in 10 minutes",
        "exam access",
        "cannot access exam",
        "can't access exam",
        "unable to access exam",
        "exam submission deadline today",
        "submission deadline today",
        "deadline is today",
    ]

    # Keywords for academic support
    academic_keywords = [
        "assignment",
        "exam",
        "quiz",
        "certificate",
        "coursework",
        "grades",
        "mathematics",
        "study",
        "explain",
        "practice questions",
        "exam preparation",
        "how to prepare",
    ]

    # 1. Course access issues
    if any(word in text for word in course_access_keywords):
        category = "Course Access Issue"
        priority = "High"
        action = (
            "Verify payment and enrollment status, "
            "then check course or batch access."
        )

    # 2. Payment issues
    elif any(word in text for word in payment_keywords):
        category = "Payment Issue"
        priority = "High"
        action = (
            "Review the payment transaction and billing "
            "records, then assist with the issue."
        )

    # 3. Urgent academic problems
    elif any(word in text for word in urgent_academic_keywords):
        category = "Academic Support"
        priority = "High"
        action = (
            "Urgently verify the exam schedule and access, "
            "then help the student resolve the issue."
        )

    # 4. Account issues
    elif any(word in text for word in account_keywords):
        category = "Account Issue"
        priority = "Medium"
        action = (
            "Verify the student's account and help resolve "
            "the login or registered email issue."
        )

    # 5. Routine academic support
    elif any(word in text for word in academic_keywords):
        category = "Academic Support"
        priority = "Medium"
        action = (
            "Review the academic issue and guide the student "
            "to the appropriate support resource."
        )

    # 6. Other questions
    else:
        category = "General Inquiry"
        priority = "Low"
        action = (
            "Review the student's question and provide "
            "the relevant information."
        )

    return {
        "ticket": ticket_text,
        "category": category,
        "priority": priority,
        "recommended_action": action,
    }