
import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Check your .env file."
    )

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.8-flash"

ALLOWED_CATEGORIES = {
    "Course Access Issue",
    "Payment Issue",
    "Account Issue",
    "Academic Support",
    "General Inquiry",
}

ALLOWED_PRIORITIES = {"High", "Medium", "Low"}


def triage_ticket_with_llm(ticket_text):
    """Classify a student support ticket using Gemini."""

    if not isinstance(ticket_text, str) or not ticket_text.strip():
        raise ValueError("Ticket text cannot be empty.")

    prompt = f"""
You are a student support ticket classification assistant.

Classify the ticket using the rules below.

Return ONLY a valid JSON object with these keys:
category, priority, recommended_action

Allowed categories:
- Course Access Issue: course, batch, lesson, or material access
- Payment Issue: failed payment, refund, billing, or deducted money
- Account Issue: login, password, or registered account problems
- Academic Support: assignments, quizzes, grades, study help,
  exam preparation, or academic concepts
- General Inquiry: anything that does not fit the other categories

Allowed priorities: High, Medium, Low

Priority rules:
- High: course/batch access blocking course use, urgent payment
  problems, or imminent exam-access/submission emergencies.
- Medium: routine login/password issues and academic issues
  with a clearly stated deadline that is not an imminent exam
  access emergency.
- Low: routine study questions, practice questions, general
  exam preparation, and non-urgent general inquiries.

Important:
- Do not mark routine study questions High just because they
  mention an exam or mathematics.
- Do not mark an exam-access emergency Low.
- Use only the information in the ticket.
- Do not claim that a payment has been verified.
- Recommend verification when details are missing.
- Make the recommended action practical and specific.
- Return JSON only, without Markdown.

Ticket:
{ticket_text}
"""

    try:
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
            "category",
            "priority",
            "recommended_action",
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

        return {
            "ticket": ticket_text,
            "category": result["category"],
            "priority": result["priority"],
            "recommended_action": result["recommended_action"].strip(),
        }

    except json.JSONDecodeError as exc:
        raise ValueError("Gemini returned invalid JSON.") from exc