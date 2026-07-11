#!/usr/bin/env python3
"""Generate Day 02-90 blog drafts from the topic calendar.

The goal is not to replace a human final edit. It creates a complete,
publishable first pass for every day: Markdown, metadata, topic-specific
examples, and editable SVG graphics that can be rendered to PNG.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOPICS_PATH = ROOT / "topics" / "topics.json"
BLOGS_DIR = ROOT / "blogs"


PALETTES = [
    ("#ecfeff", "#0f172a", "#06b6d4", "#f9f871"),
    ("#f0fdf4", "#064e3b", "#22c55e", "#38bdf8"),
    ("#fff7ed", "#7c2d12", "#f97316", "#a78bfa"),
    ("#f5f3ff", "#3b0764", "#8b5cf6", "#22d3ee"),
    ("#fff1f2", "#881337", "#fb7185", "#facc15"),
    ("#f8fafc", "#111827", "#64748b", "#34d399"),
]


CATEGORY_FRAMEWORKS = {
    "AI Foundations": ["Concept", "Example", "Mental model", "Try it"],
    "AI Trends": ["Trend", "Why now", "What changes", "Builder move"],
    "Prompting": ["Goal", "Context", "Constraints", "Output"],
    "RAG and Search": ["Question", "Retrieve", "Ground answer", "Cite"],
    "Agentic AI": ["Goal", "Plan", "Act with tools", "Observe"],
    "AI Protocols": ["App", "Protocol", "Tool", "Result"],
    "AI Coding": ["Task", "Repo context", "Patch", "Tests"],
    "AI Operations": ["Signal", "Summarize", "Act", "Verify"],
    "Production AI": ["Prompt", "Eval", "Deploy", "Monitor"],
    "Multimodal AI": ["Input", "Understand", "Generate", "Review"],
    "Generative Media": ["Prompt", "Reference", "Generate", "Edit"],
    "AI Tools": ["Workflow", "AI assist", "Human review", "Output"],
    "AI Marketing": ["Audience", "Message", "Channel", "Measure"],
    "AI Commerce": ["Intent", "Product data", "Agent choice", "Checkout"],
    "Business AI": ["Process", "AI assist", "Controls", "ROI"],
    "AI Industries": ["Use case", "Risk", "Workflow", "Oversight"],
    "AI Security": ["Threat", "Detection", "Control", "Response"],
    "AI Governance": ["Policy", "Risk tier", "Review", "Audit"],
    "AI Models": ["Architecture", "Tradeoff", "Use case", "Limit"],
    "AI Infrastructure": ["Hardware", "Runtime", "Cost", "Scale"],
    "AI Strategy": ["Goal", "Choice", "Metric", "Rollout"],
    "Future of Work": ["Delegate", "Review", "Approve", "Improve"],
    "Data and AI": ["Data", "Question", "Analysis", "Decision"],
    "Enterprise AI": ["Workflow", "Integration", "Permissions", "Scale"],
    "Career and Learning": ["Skill", "Practice", "Project", "Proof"],
    "Future of AI": ["Interface", "Agent", "Workflow", "Human"],
    "Series Finale": ["Models", "Agents", "Tools", "Judgment"],
}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def wrap_text(text: str, max_chars: int = 48, max_lines: int = 2) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if current and len(candidate) > max_chars:
            lines.append(" ".join(current))
            current = [word]
            if len(lines) == max_lines - 1:
                break
        else:
            current.append(word)

    remaining = words[sum(len(line.split()) for line in lines) :]
    if len(lines) == max_lines - 1 and remaining:
        final = " ".join(remaining)
        if len(final) > max_chars:
            final = final[: max_chars - 3].rstrip() + "..."
        lines.append(final)
    elif current:
        lines.append(" ".join(current))

    return lines[:max_lines]


def safe_title(title: str) -> str:
    return title


def palette(day: int) -> tuple[str, str, str, str]:
    return PALETTES[(day - 1) % len(PALETTES)]


def framework(category: str) -> list[str]:
    return CATEGORY_FRAMEWORKS.get(category, ["Idea", "Workflow", "Example", "Guardrail"])


def category_intro(category: str) -> str:
    intros = {
        "AI Foundations": "This is one of those foundation ideas that makes every later AI topic less foggy.",
        "AI Trends": "Trends are useful only when they help you decide what to build, learn, or ignore.",
        "Prompting": "Prompting is not about magic words. It is about giving the model a useful operating brief.",
        "RAG and Search": "RAG is how we stop asking models to remember everything and start giving them useful source material.",
        "Agentic AI": "Agentic AI is where models stop being only answer machines and start becoming workflow machines.",
        "AI Coding": "For developers, AI becomes valuable when it works with the repo, the tests, and reality.",
        "Production AI": "Production AI is where demos meet monitoring, costs, edge cases, and users with creative typing habits.",
        "AI Governance": "Governance is the part that feels boring until it saves the product, the user, or the company.",
        "AI Security": "AI security matters because models can be helpful, gullible, and very confident at the same time.",
        "Business AI": "Business AI works best when it improves a real workflow instead of floating around as a shiny demo.",
        "Data and AI": "AI feels smart only when the data underneath it is not quietly doing interpretive dance.",
        "Future of Work": "The future of work is less about replacing everyone and more about redesigning who does what.",
    }
    return intros.get(category, "This topic matters because it turns AI from a buzzword into something you can actually use.")


def use_case_for(topic: dict) -> str:
    category = topic["category"]
    title = safe_title(topic["title"])
    if "coding" in category.lower() or "code" in title.lower():
        return "Use it to speed up code understanding, generate safer first drafts, and create tests that catch boring but expensive mistakes."
    if "RAG" in category or "Search" in category or "document" in title.lower():
        return "Use it when answers need to be grounded in your own documents instead of the model's memory and good intentions."
    if "Agent" in category or "agent" in title.lower():
        return "Use it for multi-step workflows where the AI needs to plan, call tools, check results, and continue."
    if "Security" in category:
        return "Use it to detect risk earlier, but keep humans and deterministic controls in charge of final decisions."
    if "Marketing" in category:
        return "Use it to turn one clear idea into drafts, variations, summaries, and channel-specific content without losing the human point of view."
    if "Commerce" in category:
        return "Use it to help users compare options, understand products, and move from intent to confident purchase."
    if "Governance" in category:
        return "Use it to build trust, reduce risk, and make sure AI systems do not become unsupervised interns with production access."
    if "Data" in category:
        return "Use it to ask better questions of messy data, generate analysis steps, and explain findings in plain language."
    return "Use it to understand what AI can actually do, where it fails, and how to design better workflows around it."


def mini_lab(topic: dict) -> str:
    title = safe_title(topic["title"])
    category = topic["category"]
    if "Prompting" in category or "Context" in title:
        return """```text
Task:
Explain this topic to a beginner.

Context:
<paste source notes, docs, or examples here>

Constraints:
- Use simple language.
- Include one practical example.
- Mention one common mistake.
- End with a checklist.

Output:
Markdown with headings and bullet points.
```"""
    if "RAG" in category or "Search" in category:
        return """```python
documents = [
    "Refunds are available within 14 days.",
    "Enterprise plans include SSO and audit logs.",
    "Password resets are handled from Account Settings."
]

query = "Can enterprise users get audit logs?"

matches = [doc for doc in documents if "audit" in doc.lower() or "enterprise" in doc.lower()]
print("\\n".join(matches))
```"""
    if "AI Coding" in category:
        return """```text
Ask the AI for:
1. A short explanation of the existing code.
2. A small change plan.
3. The patch.
4. Tests.
5. A review of its own diff.

Rule:
No tests, no trust. The compiler gets a vote.
```"""
    if "Security" in category:
        return """```text
Security review prompt:

Identify:
- possible data leaks
- unsafe tool calls
- prompt injection risks
- missing permission checks
- logging mistakes

Return severity, evidence, and suggested fix.
```"""
    if "Data" in category:
        return """```sql
-- Start boring. Boring is how dashboards stay alive.
SELECT
  category,
  COUNT(*) AS total_events
FROM events
GROUP BY category
ORDER BY total_events DESC;
```"""
    if "Governance" in category:
        return """```text
AI risk checklist:
- What data goes in?
- Who sees the output?
- Can the AI take action?
- How is output validated?
- Who is accountable when it fails?
```"""
    return f"""```text
Mini lab:
1. Pick one workflow related to "{title}".
2. Write the current manual steps.
3. Mark which steps need judgment and which are repetitive.
4. Let AI draft only the repetitive parts.
5. Add a human review checkpoint before anything important happens.
```"""


def example_file(topic: dict) -> tuple[str, str]:
    day = topic["day"]
    title = safe_title(topic["title"])
    category = topic["category"]
    if "RAG" in category or "Search" in category:
        return (
            "mini_retrieval_demo.py",
            f'''#!/usr/bin/env python3
"""Mini retrieval demo for Day {day}: {title}."""

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
        print(f"score={{score}} | {{document}}")
''',
        )
    if "Data" in category:
        return (
            "simple_analysis.py",
            f'''#!/usr/bin/env python3
"""Simple analysis demo for Day {day}: {title}."""

events = [
    {{"category": "signup", "value": 1}},
    {{"category": "signup", "value": 1}},
    {{"category": "upgrade", "value": 99}},
    {{"category": "cancel", "value": 1}},
]

totals = {{}}
for event in events:
    totals[event["category"]] = totals.get(event["category"], 0) + event["value"]

for category, total in sorted(totals.items()):
    print(f"{{category}}: {{total}}")
''',
        )
    if "AI Coding" in category or "Production AI" in category:
        return (
            "ai_workflow_checklist.py",
            f'''#!/usr/bin/env python3
"""Workflow checklist for Day {day}: {title}."""

checks = [
    "Clear goal",
    "Relevant context",
    "Small change",
    "Tests or validation",
    "Human review",
]

for index, check in enumerate(checks, start=1):
    print(f"{{index}}. {{check}}")
''',
        )
    return (
        "practical_checklist.md",
        f"""# Practical Checklist

Topic: {title}

- What problem does this solve?
- What input does the AI need?
- What should the output look like?
- How will we verify the result?
- Where should a human stay in the loop?
""",
    )


def hero_svg(topic: dict) -> str:
    day = topic["day"]
    title = safe_title(topic["title"])
    category = topic["category"]
    bg, dark, accent, pop = palette(day)
    title_lines = wrap_text(title, max_chars=44, max_lines=2)
    title_svg = "\n".join(
        f'  <text x="70" y="{166 + i * 56}" font-family="Arial, sans-serif" font-size="50" font-weight="900" fill="#111827">{esc(line)}</text>'
        for i, line in enumerate(title_lines)
    )
    subtitle_y = 214 + (len(title_lines) - 1) * 56
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="788" viewBox="0 0 1400 788" role="img" aria-labelledby="title desc">
  <title id="title">Day {day}: {esc(title)}</title>
  <desc id="desc">Modern blog hero graphic for {esc(title)}.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{bg}"/>
      <stop offset="0.55" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#eef2ff"/>
    </linearGradient>
    <linearGradient id="cardGlow" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{accent}"/>
      <stop offset="1" stop-color="{pop}"/>
    </linearGradient>
    <linearGradient id="darkGlow" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#111827"/>
      <stop offset="1" stop-color="{dark}"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#0f172a" flood-opacity="0.18"/>
    </filter>
  </defs>
  <rect width="1400" height="788" fill="url(#bg)"/>
  <path d="M1060 -40 C1260 80 1325 250 1440 380 L1440 0 Z" fill="{accent}" opacity="0.22"/>
  <path d="M-70 620 C150 505 295 610 415 780 L-70 780 Z" fill="{pop}" opacity="0.25"/>
  <g opacity="0.20" stroke="{accent}" stroke-width="2">
    <path d="M75 330 H610"/><path d="M75 570 H660"/><path d="M115 302 V612"/><path d="M520 302 V612"/>
  </g>
  <rect x="70" y="58" width="310" height="48" rx="16" fill="#111827"/>
  <text x="94" y="90" font-family="Arial, sans-serif" font-size="24" font-weight="900" fill="#ffffff">DAY {day:02d} / 90 DAYS OF AI</text>
{title_svg}
  <text x="73" y="{subtitle_y}" font-family="Arial, sans-serif" font-size="25" font-weight="700" fill="#475569">{esc(category)} made visual, practical, and snackable.</text>
  <g transform="translate(70 {subtitle_y + 34})">
    <rect x="0" y="0" width="172" height="42" rx="15" fill="{accent}"/>
    <text x="24" y="28" font-family="Arial, sans-serif" font-size="18" font-weight="900" fill="#ffffff">NO FLUFF</text>
    <rect x="188" y="0" width="178" height="42" rx="15" fill="{pop}"/>
    <text x="213" y="28" font-family="Arial, sans-serif" font-size="18" font-weight="900" fill="#111827">REAL EXAMPLES</text>
  </g>
  <g filter="url(#shadow)">
    <rect x="90" y="400" width="245" height="142" rx="28" fill="#ffffff" stroke="{accent}" stroke-width="4"/>
    <rect x="390" y="360" width="245" height="222" rx="34" fill="url(#cardGlow)" opacity="0.96"/>
    <rect x="690" y="400" width="245" height="142" rx="28" fill="#ffffff" stroke="{pop}" stroke-width="4"/>
    <rect x="990" y="360" width="245" height="222" rx="34" fill="url(#darkGlow)" opacity="0.98"/>
  </g>
  <g font-family="Arial, sans-serif">
    <text x="125" y="446" font-size="26" font-weight="900" fill="{accent}">01</text>
    <text x="212" y="462" text-anchor="middle" font-size="25" font-weight="900" fill="#111827">Learn</text>
    <text x="212" y="499" text-anchor="middle" font-size="19" fill="#475569">plain English</text>
    <text x="425" y="418" font-size="28" font-weight="900" fill="#ffffff">02</text>
    <text x="512" y="472" text-anchor="middle" font-size="28" font-weight="900" fill="#ffffff">Build</text>
    <text x="512" y="512" text-anchor="middle" font-size="20" font-weight="700" fill="#f8fafc">tiny workflow</text>
    <text x="725" y="446" font-size="26" font-weight="900" fill="{accent}">03</text>
    <text x="812" y="462" text-anchor="middle" font-size="25" font-weight="900" fill="#111827">Check</text>
    <text x="812" y="499" text-anchor="middle" font-size="19" fill="#475569">trust, but test</text>
    <text x="1025" y="418" font-size="28" font-weight="900" fill="{pop}">04</text>
    <text x="1112" y="472" text-anchor="middle" font-size="28" font-weight="900" fill="#ffffff">Ship</text>
    <text x="1112" y="512" text-anchor="middle" font-size="20" font-weight="700" fill="#e5e7eb">with receipts</text>
  </g>
  <g stroke="#111827" stroke-width="8" stroke-linecap="round" opacity="0.52">
    <path d="M345 471 H378"/><path d="M645 471 H678"/><path d="M945 471 H978"/>
  </g>
  <rect x="70" y="650" width="640" height="70" rx="24" fill="#111827"/>
  <text x="105" y="694" font-family="Arial, sans-serif" font-size="23" font-weight="900" fill="#ffffff">Useful AI, minus the buzzword fog.</text>
</svg>
'''


def flow_svg(topic: dict) -> str:
    day = topic["day"]
    title = safe_title(topic["title"])
    category = topic["category"]
    bg, dark, accent, pop = palette(day)
    steps = framework(category)
    while len(steps) < 4:
        steps.append("Review")
    card_specs = [
        (90, "#ffffff", accent, "#111827", accent, "start clear"),
        (355, accent, accent, "#ffffff", "#ffffff", "add context"),
        (620, "#ffffff", pop, "#111827", accent, "make it work"),
        (885, "#111827", "#111827", "#ffffff", pop, "check reality"),
    ]
    card_svg: list[str] = []
    for index, (x, fill, stroke, text_fill, number_fill, caption) in enumerate(card_specs, start=1):
        label_lines = wrap_text(steps[index - 1], max_chars=13, max_lines=2)
        label_start_y = 350 if len(label_lines) == 1 else 340
        labels = "\n".join(
            f'<text x="{x + 115}" y="{label_start_y + line_index * 27}" text-anchor="middle" font-size="24" font-weight="900" fill="{text_fill}">{esc(line)}</text>'
            for line_index, line in enumerate(label_lines)
        )
        card_svg.append(
            f'''    <g filter="url(#shadow)">
      <rect x="{x}" y="288" width="230" height="132" rx="26" fill="{fill}" stroke="{stroke}" stroke-width="4"/>
    </g>
    <text x="{x + 31}" y="322" font-size="24" font-weight="900" fill="{number_fill}">{index:02d}</text>
{labels}
    <text x="{x + 115}" y="392" text-anchor="middle" font-size="18" font-weight="700" fill="{text_fill}" opacity="0.78">{caption}</text>'''
        )
    cards = "\n".join(card_svg)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675" role="img" aria-labelledby="title desc">
  <title id="title">Day {day} concept flow</title>
  <desc id="desc">A four-step concept flow for {esc(title)}.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{bg}"/>
      <stop offset="0.60" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#eef2ff"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="15" flood-color="#0f172a" flood-opacity="0.16"/>
    </filter>
  </defs>
  <rect width="1200" height="675" fill="url(#bg)"/>
  <path d="M920 -70 C1080 40 1135 170 1240 310 L1240 -70 Z" fill="{accent}" opacity="0.20"/>
  <path d="M-50 520 C145 430 315 505 415 720 L-50 720 Z" fill="{pop}" opacity="0.24"/>
  <rect x="55" y="55" width="1090" height="565" rx="30" fill="#ffffff" opacity="0.82" stroke="#ffffff" stroke-width="3"/>
  <rect x="90" y="88" width="220" height="42" rx="15" fill="#111827"/>
  <text x="114" y="116" font-family="Arial, sans-serif" font-size="21" font-weight="900" fill="#ffffff">DAY {day:02d} FLOW</text>
  <text x="95" y="176" font-family="Arial, sans-serif" font-size="34" font-weight="900" fill="#111827">{esc(category)}</text>
  <text x="95" y="214" font-family="Arial, sans-serif" font-size="20" font-weight="700" fill="#52606d">{esc(title)}</text>
  <g font-family="Arial, sans-serif">
{cards}
    <path d="M323 354 H350" stroke="#111827" stroke-width="6" stroke-linecap="round" opacity="0.45"/>
    <path d="M588 354 H615" stroke="#111827" stroke-width="6" stroke-linecap="round" opacity="0.45"/>
    <path d="M853 354 H880" stroke="#111827" stroke-width="6" stroke-linecap="round" opacity="0.45"/>
  </g>
  <rect x="95" y="500" width="760" height="64" rx="20" fill="#111827"/>
  <text x="130" y="540" font-family="Arial, sans-serif" font-size="22" font-weight="900" fill="#ffffff">Builder rule: validate before celebration.</text>
  <rect x="880" y="500" width="235" height="64" rx="20" fill="{pop}"/>
  <text x="914" y="540" font-family="Arial, sans-serif" font-size="22" font-weight="900" fill="#111827">signal &gt; hype</text>
</svg>
'''


def metadata(topic: dict, slug: str) -> dict:
    title = safe_title(topic["title"])
    return {
        "day": topic["day"],
        "title": title,
        "slug": slug,
        "series": "90 Days of AI",
        "category": topic["category"],
        "status": "draft-ready",
        "target_reader": "Beginners, builders, software engineers, creators, and professionals who want practical AI fluency.",
        "meta_title": title,
        "meta_description": topic["angle"],
        "keywords": topic.get("keywords", []),
        "canonical_platform": "Hashnode",
        "linkedin_post_angle": f"Day {topic['day']} of 90 Days of AI: {title}. A practical breakdown with examples, diagrams, and no buzzword fog machine.",
        "assets": ["assets/hero.png", "assets/concept-flow.png"],
        "examples": ["examples/" + example_file(topic)[0]],
    }


def blog_markdown(topic: dict, next_title: str | None) -> str:
    day = topic["day"]
    title = safe_title(topic["title"])
    category = topic["category"]
    angle = topic["angle"]
    keywords = ", ".join(topic.get("keywords", []))
    use_case = use_case_for(topic)
    lab = mini_lab(topic)
    next_line = f"\nTomorrow: **{safe_title(next_title)}**.\n" if next_title else "\nThat completes the 90-day run. The confetti is metaphorical, but deserved.\n"
    steps = framework(category)
    while len(steps) < 4:
        steps.append("Review")

    return f"""# {title}

![{title} hero](assets/hero.png)

Welcome to **Day {day} of 90 Days of AI**.

Today we are tackling **{title}**.

The mission is simple: understand the idea, see where it is useful, avoid the shiny-demo trap, and leave with something practical you can try.

No lab coat required. No buzzword fog machine. Just the useful stuff.

## The 30-second version

{angle}

Here is the plain-English version:

> {title} is worth learning because it changes how people build, automate, create, decide, or work with AI systems.

The trick is not memorizing vocabulary. The trick is knowing:

- what problem it solves,
- what input it needs,
- what output it produces,
- where it fails,
- and how to verify the result before trusting it.

That last part matters. AI confidence can look very polished while being completely wrong. Basically, a PowerPoint slide with better posture.

## Why this topic matters now

{category_intro(category)}

AI is moving from **chat window** to **workflow layer**.

That means the interesting question is no longer:

> Can AI answer this?

The better question is:

> Can AI help complete this workflow safely, repeatably, and with less human busywork?

For **{category}**, this matters because the winners will not be the people who use the fanciest tool once. The winners will be the people who turn the idea into a repeatable system.

## The core mental model

![{title} concept flow](assets/concept-flow.png)

Use this four-step frame:

1. **{steps[0]}** - understand the job before asking AI to do anything.
2. **{steps[1]}** - give the model the right context or source material.
3. **{steps[2]}** - let AI generate, transform, search, plan, or assist.
4. **{steps[3]}** - validate before the output touches anything important.

That final step is where many AI demos go to become cautionary tales.

## A noob-friendly explanation

Imagine you hired a very fast assistant.

This assistant has read a shocking amount of text, knows many patterns, and can produce a useful first draft quickly.

But the assistant has three quirks:

- it may not know your exact situation,
- it may sound confident even when uncertain,
- and it needs clear instructions or it starts improvising like a meeting with no agenda.

So your job is not to worship the assistant.

Your job is to manage the workflow.

For this topic, that means:

- define the task,
- provide the right context,
- ask for a specific output,
- check the result,
- and improve the loop.

That is practical AI. Less sparkle, more systems thinking.

## Where this shows up in real life

{use_case}

Common places you will see this:

- internal productivity tools,
- developer workflows,
- customer support,
- content creation,
- research and analysis,
- business operations,
- education and training,
- and automation pipelines.

The pattern is usually the same:

```text
messy input -> AI assistance -> structured output -> validation -> human or system action
```

If you remember that pattern, half the AI landscape becomes easier to understand.

## Practical example

Here is a small hands-on example related to this topic:

{lab}

This example is intentionally simple.

Simple examples are underrated. They let you understand the moving parts before the enterprise architecture arrives wearing a blazer.

## A better prompt to use

Try this prompt pattern:

```text
You are helping me understand and apply: {title}

Goal:
Explain the topic in beginner-friendly language and show how to use it in a practical workflow.

Context:
Audience: beginners and builders
Use case: <describe your real workflow here>

Constraints:
- Use simple language.
- Give one practical example.
- Mention common mistakes.
- Include a validation checklist.
- Do not overhype the topic.

Output:
Markdown with headings, bullet points, and one example.
```

This works because it gives the model a job, context, constraints, and a format.

Without that, you may get a dramatic essay that sounds useful until you try to implement it.

## Common mistakes

Watch out for these:

- **Mistaking a demo for a system.** A demo can impress people. A system survives Monday morning.
- **Skipping validation.** AI output should be checked, especially if it affects users, money, security, health, or reputation.
- **Using vague prompts.** Vague input creates vague output with confident eyebrows.
- **Ignoring data quality.** If the input is messy, the output may become professionally formatted nonsense.
- **Automating too much too soon.** Start with assistive workflows before handing over the steering wheel.

The goal is not to avoid AI.

The goal is to use it like a builder instead of a gambler with Wi-Fi.

## Quick checklist

Before using this in a real workflow, ask:

- What exact task should AI help with?
- What context does it need?
- What should the output look like?
- How will we verify the output?
- What can go wrong?
- Who approves the final result?
- What data should not be sent to the model?
- What metric tells us this is actually useful?

If you can answer those questions, you are not just using AI.

You are designing an AI workflow.

## Keywords to remember

{keywords}

Do not memorize these like exam flashcards.

Use them as search handles. When you see these terms in tools, docs, or product announcements, you will know what mental bucket they belong to.

## Final takeaway

The big idea behind **{title}** is not hype.

It is leverage.

AI becomes useful when you connect it to a real workflow, give it the right context, and validate the result before trusting it.

Use this formula:

```text
clear task + useful context + AI assistance + validation = practical value
```

That is the difference between a toy demo and something people come back to every day.

And that is how beginners become dangerous in the good way: not by knowing every model name, but by understanding the patterns underneath.
{next_line}"""


def main() -> None:
    data = json.loads(TOPICS_PATH.read_text())
    topics = data["topics"]

    for index, topic in enumerate(topics):
        if topic["day"] == 1:
            continue
        day = topic["day"]
        title = safe_title(topic["title"])
        topic["title"] = title
        day_dir = BLOGS_DIR / f"day-{day:02d}"
        assets_dir = day_dir / "assets"
        examples_dir = day_dir / "examples"
        assets_dir.mkdir(parents=True, exist_ok=True)
        examples_dir.mkdir(parents=True, exist_ok=True)

        slug = slugify(title)
        next_title = topics[index + 1]["title"] if index + 1 < len(topics) else None

        (assets_dir / "hero.svg").write_text(hero_svg(topic), encoding="utf-8")
        (assets_dir / "concept-flow.svg").write_text(flow_svg(topic), encoding="utf-8")
        (day_dir / "metadata.json").write_text(json.dumps(metadata(topic, slug), indent=2) + "\n", encoding="utf-8")
        (day_dir / "blog.md").write_text(blog_markdown(topic, next_title), encoding="utf-8")

        example_name, example_content = example_file(topic)
        (examples_dir / example_name).write_text(example_content, encoding="utf-8")

    # Also persist sanitized title changes, if any, back to the local series copy.
    data["topics"] = topics
    TOPICS_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
