#!/usr/bin/env python3
"""Mini retrieval demo for Day 9: RAG Explained: Giving AI an Open-Book Exam."""

documents = [
    "Refunds are available within 14 days of purchase.",
    "Enterprise plans include SSO, audit logs, and priority support.",
    "Password resets are available from Account Settings.",
    "Invoices can be downloaded from the Billing page."
]

query = "Do enterprise customers get audit logs?"
keywords = set(query.lower().replace("?", "").split())

scored = []
for document in documents:
    score = sum(1 for word in keywords if word in document.lower())
    scored.append((score, document))

for score, document in sorted(scored, reverse=True):
    if score:
        print(f"score={score} | {document}")
