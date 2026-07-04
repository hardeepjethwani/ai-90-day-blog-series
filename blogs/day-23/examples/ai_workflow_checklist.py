#!/usr/bin/env python3
"""Workflow checklist for Day 23: AI Code Review: What Models Catch and What Humans Still Own."""

checks = [
    "Clear goal",
    "Relevant context",
    "Small change",
    "Tests or validation",
    "Human review",
]

for index, check in enumerate(checks, start=1):
    print(f"{index}. {check}")
