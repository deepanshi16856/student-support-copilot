
import os
import json

from dotenv import load_dotenv
from google import genai
from knowledge_base import search_knowledge_base, format_citations

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

MODEL_NAME = "gemini-3.8-flash"

ALLOWED_CATEGORIES = {
    "Course Access Issue",
    "Payment Issue",
    "Account Issue",
    "Academic Support",
    "General Inquiry",
}

ALLOWED_PRIORITIES = {"High", "Medium", "Low"}

HUMAN_REVIEW_KEYWORDS = {
    "refund", "money back", "duplicate payment",
    "angry", "furious", "complaint", "lawyer",
    "legal action", "fraud", "scam", "charged twice",
    "cancel my subscription", "still not resolved",
}


def get_routing_decision(ticket_text, priority, articles):
    """Choose whether a ticket needs human review."""

    text = ticket_text.lower()

    matched_risk = [
        word for word in HUMAN_REVIEW_KEYWORDS
        if word in text
    ]

    if matched_risk:
        return (
            "Escalate to human",
            "Sensitive or potentially disputed issue: "
            + ", ".join(matched_risk),
        )

    if priority == "High":
        return (
            "Escalate to human",
            "High-priority ticket requires human review.",
        )

    if not articles:
        return (
            "Escalate to human",
            "No matching knowledge-base article was found.",
        )

    return (
        "Eligible for auto-reply",
        "Routine ticket with a matching knowledge-base article.",
    )


def build_fallback_reply(ticket_text, articles):
    """Create a safe reply when the LLM is unavailable."""

    if not articles:
        return (
            "Thank you for contacting student support. "
            "Our support team will review your concern and assist you."
        )

    article = articles[0]

    return (
        "Hello! Thank you for contacting student support. "
        f"Regarding your concern, {article['content']} "
        "If the issue continues, please reply with the relevant "
        "details so the support team can assist you."
    )


def enrich_triage_result(ticket_text, result):
    """Add a grounded reply, citations, and routing decision."""

    articles = search_knowledge_base(ticket_text, top_k=3)
    citations = format_citations(articles)

    decision, reason = get_routing_decision(
        ticket_text,
        result.get("priority", "Medium"),
        articles,
    )

    fallback_reply = build_fallback_reply(ticket_text, articles)
    drafted_reply = fallback_reply

    # Ask Gemini to draft a response using only retrieved sources.
    if client and articles:
        sources = "\n\n".join(
            f"Source ID: {a['id']}\n"
            f"Title: {a['title']}\n"
            f"Content: {a['content']}"
            for a in articles
        )

        prompt = f"""
You are drafting a helpful student-support reply.

Use only the supplied knowledge-base sources.
Do not invent policies, promise refunds, or claim actions are completed.
Do not ask for passwords or OTPs.
Be concise, polite, and empathetic.
Return only the reply text, not JSON.
Do not include citation IDs in the reply; they will be attached separately.

Student ticket:
{ticket_text}

Knowledge-base sources:
{sources}
"""

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config={"temperature": 0.2},
            )

            if response.text and response.text.strip():
                drafted_reply = response.text.strip()

        except Exception:
            # Keep the app useful during API quota or service errors.
            drafted_reply = fallback_reply

    return {
        **result,
        "drafted_reply": drafted_reply,
        "citations": citations,
        "matched_sources": [
            {
                "id": a["id"],
                "title": a["title"],
                "source": a["source"],
            }
            for a in articles
        ],
        "routing_decision": decision,
        "escalation_reason": reason,
    }


def triage_ticket_with_llm(ticket_text):
    """Classify a ticket and enrich it with a cited draft reply."""

    if not isinstance(ticket_text, str) or not ticket_text.strip():
        raise ValueError("Ticket text cannot be empty.")

    if not client:
        raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

    prompt = f"""
You are a student support ticket classification assistant.

Return only a valid JSON object with these keys:
category, priority, recommended_action

Allowed categories:
- Course Access Issue
- Payment Issue
- Account Issue
- Academic Support
- General Inquiry

Choose the closest category based only on the ticket.
Allowed priorities: High, Medium, Low.

High: blocked course access, urgent payment problems, or imminent
exam-access emergencies.
Medium: routine account problems or academic issues with a stated deadline.
Low: routine study questions and non-urgent inquiries.

Do not mark routine study questions High just because they mention exams.
Do not claim a payment has been verified.
Make the recommended action practical and specific.
Return JSON only, without Markdown.

Ticket:
{ticket_text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0,
        },
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    result = json.loads(response.text)

    required_keys = {
        "category", "priority", "recommended_action"
    }

    if not isinstance(result, dict):
        raise ValueError("Gemini did not return a JSON object.")

    if not required_keys.issubset(result):
        raise ValueError("Gemini returned an incomplete result.")

    if result["category"] not in ALLOWED_CATEGORIES:
        raise ValueError("Gemini returned an invalid category.")

    if result["priority"] not in ALLOWED_PRIORITIES:
        raise ValueError("Gemini returned an invalid priority.")

    if (
        not isinstance(result["recommended_action"], str)
        or not result["recommended_action"].strip()
    ):
        raise ValueError("Gemini returned an invalid recommended action.")

    clean_result = {
        "ticket": ticket_text,
        "category": result["category"],
        "priority": result["priority"],
        "recommended_action": result["recommended_action"].strip(),
    }

    return enrich_triage_result(ticket_text, clean_result)