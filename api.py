
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import (
    initialize_db,
    add_analysis_method_column,
    save_ticket,
    get_all_tickets,
    update_ticket_status,
)
from triage import triage_ticket
from llm_triage import triage_ticket_with_llm


app = FastAPI(
    title="Student Support Copilot API",
    description="API for student support ticket triage, AI replies, and escalation.",
    version="1.0.0",
)

# Development frontend. Restrict this to the deployed frontend URL later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)


@app.on_event("startup")
def startup():
    initialize_db()
    add_analysis_method_column()


class TicketRequest(BaseModel):
    ticket: str = Field(min_length=3, max_length=5000)


class StatusRequest(BaseModel):
    status: Literal["Open", "In Progress", "Resolved"]


@app.get("/health")
def health():
    return {"status": "ok", "service": "Student Support Copilot API"}


@app.post("/tickets")
def create_ticket(request: TicketRequest):
    ticket_text = request.ticket.strip()

    if not ticket_text:
        raise HTTPException(status_code=422, detail="Ticket cannot be empty.")

    try:
        try:
            result = triage_ticket_with_llm(ticket_text)
            analysis_method = "Gemini LLM"
        except Exception:
            # Fall back to the existing rule-based classifier.
            result = triage_ticket(ticket_text)
            analysis_method = "Rule-based fallback"

        # Keep the database ticket text consistent with the submitted text.
        result["ticket"] = ticket_text

        ticket_id = save_ticket(result, analysis_method)

        return {
            "id": ticket_id,
            **result,
            "analysis_method": analysis_method,
            "status": "Open",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not process the ticket: {str(exc)}",
        ) from exc


@app.get("/tickets")
def list_tickets():
    return get_all_tickets() or []


@app.patch("/tickets/{ticket_id}/status")
def change_ticket_status(ticket_id: int, request: StatusRequest):
    updated = update_ticket_status(ticket_id, request.status)

    if not updated:
        raise HTTPException(status_code=404, detail="Ticket not found.")

    return {
        "id": ticket_id,
        "status": request.status,
        "message": "Ticket status updated successfully.",
    }