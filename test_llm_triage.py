
from llm_triage import triage_ticket_with_llm

ticket = "I paid for my course, but my batch is not visible."

result = triage_ticket_with_llm(ticket)

print("\n--- AI Ticket Analysis ---")
print(result)
