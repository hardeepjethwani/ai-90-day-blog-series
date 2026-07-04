#!/usr/bin/env python3
"""Simple analysis demo for Day 83: AI Data Readiness: Your Model Is Only as Good as Your Messy Database."""

events = [
    {"category": "signup", "value": 1},
    {"category": "signup", "value": 1},
    {"category": "upgrade", "value": 99},
    {"category": "cancel", "value": 1},
]

totals = {}
for event in events:
    totals[event["category"]] = totals.get(event["category"], 0) + event["value"]

for category, total in sorted(totals.items()):
    print(f"{category}: {total}")
