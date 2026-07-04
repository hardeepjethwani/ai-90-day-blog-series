#!/usr/bin/env python3
"""Simple analysis demo for Day 82: AI and BI Dashboards: Asking Data Questions in Plain English."""

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
