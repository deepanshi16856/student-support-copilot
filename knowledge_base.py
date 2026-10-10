
"""Local knowledge base for Student Support Copilot."""

KNOWLEDGE_BASE = [
    {
        "id": "KB001",
        "title": "Course and Batch Access",
        "category": "Course Access Issue",
        "source": "student_support_guide.md",
        "keywords": [
            "batch", "course", "access", "not visible",
            "enrollment", "classes", "missing course"
        ],
        "content": (
            "If a paid course or batch is not visible, verify the "
            "payment and enrollment status, confirm the correct account "
            "is being used, and check course access. If access remains "
            "unavailable, escalate to the support team. Do not claim "
            "access has been restored until verified."
        ),
    },
    {
        "id": "KB002",
        "title": "Payment Issues",
        "category": "Payment Issue",
        "source": "student_support_guide.md",
        "keywords": [
            "payment", "paid", "transaction", "failed",
            "deducted", "receipt", "money"
        ],
        "content": (
            "For payment problems, ask the student to check the "
            "transaction status and retain the transaction reference. "
            "The support team should verify the payment before confirming "
            "its status. Escalate duplicate deductions or unresolved "
            "transactions. Never request passwords or OTPs."
        ),
    },
    {
        "id": "KB003",
        "title": "Refund Requests",
        "category": "Payment Issue",
        "source": "student_support_guide.md",
        "keywords": [
            "refund", "money back", "cancel", "reimbursement"
        ],
        "content": (
            "For refund requests, collect the order or transaction "
            "reference and route the request to the authorised support "
            "team for eligibility review. Do not promise a refund or "
            "specific processing time without verified policy information."
        ),
    },
    {
        "id": "KB004",
        "title": "Account and Login Issues",
        "category": "Account Issue",
        "source": "student_support_guide.md",
        "keywords": [
            "login", "password", "account", "sign in",
            "otp", "locked", "email"
        ],
        "content": (
            "For login issues, confirm that the student is using the "
            "registered account and suggest the official password-reset "
            "process. Never ask for passwords or OTPs. Escalate if the "
            "account remains inaccessible."
        ),
    },
    {
        "id": "KB005",
        "title": "Academic Support",
        "category": "Academic Support",
        "source": "student_support_guide.md",
        "keywords": [
            "doubt", "concept", "lecture", "assignment",
            "question", "study", "academic"
        ],
        "content": (
            "For academic doubts, identify the subject, topic, and "
            "specific question. Direct the student to relevant course "
            "lessons or the available academic doubt-support channel."
        ),
    },
    {
        "id": "KB006",
        "title": "Technical Problems",
        "category": "Technical Issue",
        "source": "student_support_guide.md",
        "keywords": [
            "technical", "error", "crash", "app",
            "website", "loading", "video", "not working"
        ],
        "content": (
            "For technical problems, ask which device and browser or "
            "app the student is using, record the error, and suggest "
            "restarting or updating the app where appropriate. Escalate "
            "persistent issues with the error details."
        ),
    },
]


def search_knowledge_base(query, category=None, top_k=3):
    """Return the most relevant knowledge articles for a ticket."""
    query_words = set(query.lower().replace("-", " ").split())
    results = []

    for article in KNOWLEDGE_BASE:
        if category and article["category"].lower() != category.lower():
            continue

        searchable = (
            article["title"] + " " +
            article["category"] + " " +
            " ".join(article["keywords"]) + " " +
            article["content"]
        ).lower()

        score = sum(
            1 for word in query_words
            if len(word) > 2 and word in searchable
        )

        for keyword in article["keywords"]:
            if keyword in query.lower():
                score += 2

        if score > 0:
            results.append({**article, "score": score})

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def format_citations(articles):
    """Format source references for a drafted response."""
    if not articles:
        return "No matching knowledge-base source found."

    return "\n".join(
        f"[{article['id']}] {article['title']} — "
        f"Source: {article['source']}"
        for article in articles
    )