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
    ("#eef6ff", "#1d4ed8", "#60a5fa", "#dbeafe"),
    ("#ecfdf5", "#047857", "#34d399", "#d1fae5"),
    ("#fff7ed", "#c2410c", "#fb923c", "#ffedd5"),
    ("#f5f3ff", "#6d28d9", "#a78bfa", "#ede9fe"),
    ("#fff1f2", "#be123c", "#fb7185", "#ffe4e6"),
    ("#f8fafc", "#334155", "#94a3b8", "#e2e8f0"),
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
    bg, dark, accent, pale = palette(day)
    title_lines = wrap_text(title, max_chars=52, max_lines=2)
    title_svg = "\n".join(
        f'  <text x="70" y="{165 + i * 58}" font-family="Arial, sans-serif" font-size="52" font-weight="900" fill="#111827">{esc(line)}</text>'
        for i, line in enumerate(title_lines)
    )
    subtitle_y = 214 + (len(title_lines) - 1) * 58
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="788" viewBox="0 0 1400 788" role="img" aria-labelledby="title desc">
  <title id="title">Day {day}: {esc(title)}</title>
  <desc id="desc">Modern blog hero graphic for {esc(title)}.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{bg}"/>
      <stop offset="0.55" stop-color="#ffffff"/>
      <stop offset="1" stop-color="{pale}"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="18" stdDeviation="18" flood-color="#0f172a" flood-opacity="0.14"/>
    </filter>
  </defs>
  <rect width="1400" height="788" fill="url(#bg)"/>
  <circle cx="1130" cy="130" r="160" fill="{accent}" opacity="0.18"/>
  <circle cx="190" cy="665" r="220" fill="{accent}" opacity="0.14"/>
  <text x="70" y="90" font-family="Arial, sans-serif" font-size="26" font-weight="800" fill="{dark}">90 DAYS OF AI • DAY {day:02d}</text>
{title_svg}
  <text x="73" y="{subtitle_y}" font-family="Arial, sans-serif" font-size="25" fill="#475569">{esc(category)} made practical, visual, and slightly less allergic to fun.</text>
  <g filter="url(#shadow)">
    <rect x="90" y="330" width="230" height="145" rx="28" fill="#ffffff" stroke="{accent}" stroke-width="3"/>
    <rect x="405" y="290" width="230" height="225" rx="32" fill="{dark}" opacity="0.92"/>
    <rect x="720" y="330" width="230" height="145" rx="28" fill="#ffffff" stroke="{accent}" stroke-width="3"/>
    <rect x="1035" y="290" width="230" height="225" rx="32" fill="#111827" opacity="0.94"/>
  </g>
  <path d="M330 402 H390" stroke="#64748b" stroke-width="8" stroke-linecap="round"/><path d="M390 402 l-22 -15 v30 z" fill="#64748b"/>
  <path d="M650 402 H710" stroke="#64748b" stroke-width="8" stroke-linecap="round"/><path d="M710 402 l-22 -15 v30 z" fill="#64748b"/>
  <path d="M965 402 H1025" stroke="#64748b" stroke-width="8" stroke-linecap="round"/><path d="M1025 402 l-22 -15 v30 z" fill="#64748b"/>
  <text x="205" y="385" text-anchor="middle" font-family="Arial, sans-serif" font-size="25" font-weight="800" fill="{dark}">Understand</text>
  <text x="205" y="425" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" fill="#475569">plain English</text>
  <text x="520" y="385" text-anchor="middle" font-family="Arial, sans-serif" font-size="25" font-weight="800" fill="#ffffff">Apply</text>
  <text x="520" y="425" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" fill="#dbeafe">real workflow</text>
  <text x="835" y="385" text-anchor="middle" font-family="Arial, sans-serif" font-size="25" font-weight="800" fill="{dark}">Validate</text>
  <text x="835" y="425" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" fill="#475569">trust, but test</text>
  <text x="1150" y="385" text-anchor="middle" font-family="Arial, sans-serif" font-size="25" font-weight="800" fill="#ffffff">Ship</text>
  <text x="1150" y="425" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" fill="#e5e7eb">with guardrails</text>
  <rect x="70" y="635" width="600" height="76" rx="24" fill="#111827"/>
  <text x="105" y="683" font-family="Arial, sans-serif" font-size="24" font-weight="800" fill="#ffffff">Useful AI, minus the buzzword fog.</text>
</svg>
'''


def flow_svg(topic: dict) -> str:
    day = topic["day"]
    title = safe_title(topic["title"])
    category = topic["category"]
    bg, dark, accent, pale = palette(day)
    steps = framework(category)
    while len(steps) < 4:
        steps.append("Review")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675" role="img" aria-labelledby="title desc">
  <title id="title">Day {day} concept flow</title>
  <desc id="desc">A four-step concept flow for {esc(title)}.</desc>
  <rect width="1200" height="675" fill="{bg}"/>
  <rect x="55" y="55" width="1090" height="565" rx="28" fill="#ffffff" stroke="{pale}" stroke-width="3"/>
  <text x="95" y="118" font-family="Arial, sans-serif" font-size="36" font-weight="900" fill="#111827">Day {day:02d} Flow: {esc(category)}</text>
  <text x="95" y="158" font-family="Arial, sans-serif" font-size="21" fill="#52606d">{esc(title)}</text>
  <g font-family="Arial, sans-serif">
    <rect x="95" y="270" width="190" height="120" rx="22" fill="{pale}" stroke="{accent}" stroke-width="3"/>
    <text x="190" y="320" text-anchor="middle" font-size="25" font-weight="800" fill="{dark}">1. {esc(steps[0])}</text>
    <text x="190" y="354" text-anchor="middle" font-size="18" fill="#475569">start clear</text>
    <rect x="365" y="270" width="190" height="120" rx="22" fill="#f8fafc" stroke="{accent}" stroke-width="3"/>
    <text x="460" y="320" text-anchor="middle" font-size="25" font-weight="800" fill="{dark}">2. {esc(steps[1])}</text>
    <text x="460" y="354" text-anchor="middle" font-size="18" fill="#475569">add context</text>
    <rect x="635" y="270" width="190" height="120" rx="22" fill="{pale}" stroke="{accent}" stroke-width="3"/>
    <text x="730" y="320" text-anchor="middle" font-size="25" font-weight="800" fill="{dark}">3. {esc(steps[2])}</text>
    <text x="730" y="354" text-anchor="middle" font-size="18" fill="#475569">make it work</text>
    <rect x="905" y="270" width="190" height="120" rx="22" fill="#111827" stroke="#111827" stroke-width="3"/>
    <text x="1000" y="320" text-anchor="middle" font-size="25" font-weight="800" fill="#ffffff">4. {esc(steps[3])}</text>
    <text x="1000" y="354" text-anchor="middle" font-size="18" fill="#e5e7eb">check reality</text>
    <path d="M285 330 H355" stroke="#64748b" stroke-width="5" stroke-linecap="round"/><path d="M355 330 l-16 -11 v22 z" fill="#64748b"/>
    <path d="M555 330 H625" stroke="#64748b" stroke-width="5" stroke-linecap="round"/><path d="M625 330 l-16 -11 v22 z" fill="#64748b"/>
    <path d="M825 330 H895" stroke="#64748b" stroke-width="5" stroke-linecap="round"/><path d="M895 330 l-16 -11 v22 z" fill="#64748b"/>
  </g>
  <rect x="95" y="500" width="770" height="62" rx="18" fill="#111827"/>
  <text x="130" y="540" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#ffffff">Builder rule: if it affects users, add validation before celebration.</text>
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
