#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOPICS_PATH = ROOT / "topics" / "topics.json"
KAPISTRA_SOURCE = ROOT / "brand" / "kapistra-watermark.png"
KAPISTRA_LOCAL_NAME = "kapistra-watermark.png"


PALETTES = [
    ("#ff3b30", "#ffb347", "#2b0505"),
    ("#3b82f6", "#22d3ee", "#020617"),
    ("#f97316", "#facc15", "#120703"),
    ("#8b5cf6", "#06b6d4", "#08051f"),
    ("#22c55e", "#84cc16", "#03130a"),
    ("#ec4899", "#fb7185", "#160412"),
]


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def wrap_title(text: str, max_chars: int = 27, max_lines: int = 3) -> list[str]:
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

    used = sum(len(line.split()) for line in lines)
    remaining = words[used:]
    if len(lines) == max_lines - 1 and remaining:
        final = " ".join(remaining)
        if len(final) > max_chars:
            final = final[: max_chars - 3].rstrip() + "..."
        lines.append(final)
    elif current:
        lines.append(" ".join(current))

    return lines[:max_lines]


def category_label(category: str) -> str:
    return category.upper().replace(" AND ", " & ")


def svg_for(topic: dict) -> str:
    day = int(topic["day"])
    title = topic["title"]
    category = topic["category"]
    accent, accent_2, deep = PALETTES[(day - 1) % len(PALETTES)]
    title_lines = wrap_title(title)
    font_size = 86 if len(title_lines) <= 2 else 74
    line_gap = 92 if len(title_lines) <= 2 else 78
    title_y = 310
    title_svg = "\n".join(
        f'<text x="110" y="{title_y + i * line_gap}" font-family="Arial Black, Arial, sans-serif" font-size="{font_size}" font-weight="900" fill="#ffffff">{esc(line)}</text>'
        for i, line in enumerate(title_lines)
    )
    underline_y = title_y + (len(title_lines) - 1) * line_gap + 30
    subtitle_y = underline_y + 82
    topic_word = re.sub(r"[^A-Za-z0-9 ]", "", title).split()
    punch = "BEGINNER FRIENDLY. BUILDER APPROVED."
    if topic_word:
        punch = f"{category_label(category)} • NO FLUFF, JUST SIGNAL"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="840" viewBox="0 0 1600 840" role="img" aria-labelledby="title desc">
  <title id="title">Day {day:02d} cover - {esc(title)}</title>
  <desc id="desc">Hashnode cover image for the 90 Days of AI series.</desc>
  <defs>
    <radialGradient id="glow" cx="20%" cy="35%" r="80%">
      <stop offset="0" stop-color="{accent}" stop-opacity="0.45"/>
      <stop offset="0.45" stop-color="{deep}" stop-opacity="0.75"/>
      <stop offset="1" stop-color="#020205"/>
    </radialGradient>
    <linearGradient id="slash" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{accent_2}" stop-opacity="0.95"/>
      <stop offset="1" stop-color="{accent}" stop-opacity="0.25"/>
    </linearGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#000000" flood-opacity="0.35"/>
    </filter>
    <filter id="textShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="4" dy="5" stdDeviation="3" flood-color="#000000" flood-opacity="0.75"/>
    </filter>
  </defs>
  <rect width="1600" height="840" fill="url(#glow)"/>
  <rect width="1600" height="840" fill="#030305" opacity="0.35"/>
  <path d="M970 -80 C1270 140 1400 420 1610 655 L1610 840 L1220 840 C1120 630 1030 390 840 150 Z" fill="#111827" opacity="0.72"/>
  <path d="M1390 60 C1210 160 1090 300 1035 475" fill="none" stroke="url(#slash)" stroke-width="70" stroke-linecap="round" opacity="0.88"/>
  <path d="M1475 115 C1290 195 1165 330 1105 520" fill="none" stroke="#ffffff" stroke-width="22" stroke-linecap="round" opacity="0.42"/>
  <g opacity="0.10">
    <rect x="930" y="235" width="170" height="55" fill="#ffffff"/>
    <rect x="1085" y="335" width="170" height="55" fill="#ffffff"/>
    <rect x="1015" y="435" width="170" height="55" fill="#ffffff"/>
    <rect x="1185" y="535" width="170" height="55" fill="#ffffff"/>
  </g>
  <image href="{KAPISTRA_LOCAL_NAME}" x="1185" y="295" width="285" height="285" opacity="0.16"/>
  <g filter="url(#textShadow)">
    <text x="110" y="105" font-family="Arial, sans-serif" font-size="38" font-style="italic" font-weight="800" fill="#ffffff">Learn with HJ</text>
    <text x="110" y="178" font-family="Arial, sans-serif" font-size="34" font-weight="900" fill="{accent_2}">90 DAYS OF AI</text>
    <text x="405" y="178" font-family="Arial, sans-serif" font-size="34" font-weight="900" fill="#ffffff">• DAY {day:02d}</text>
    {title_svg}
  </g>
  <rect x="110" y="{underline_y}" width="520" height="10" rx="5" fill="{accent}"/>
  <rect x="110" y="{underline_y + 18}" width="270" height="10" rx="5" fill="{accent_2}"/>
  <text x="110" y="{subtitle_y}" font-family="Arial Black, Arial, sans-serif" font-size="42" font-weight="900" fill="#ffffff" filter="url(#textShadow)">THE PRACTICAL GUIDE + CHEAT SHEET</text>
  <text x="110" y="{subtitle_y + 58}" font-family="Arial, sans-serif" font-size="30" font-weight="800" fill="{accent_2}">{esc(punch)}</text>
  <g transform="translate(110 720)">
    <rect x="0" y="0" width="42" height="42" rx="9" fill="#0a66c2"/><text x="21" y="29" text-anchor="middle" font-family="Arial" font-size="22" font-weight="900" fill="#ffffff">in</text>
    <rect x="56" y="0" width="42" height="42" rx="9" fill="#111111"/><text x="77" y="29" text-anchor="middle" font-family="Arial" font-size="22" font-weight="900" fill="#ffffff">X</text>
    <rect x="112" y="0" width="42" height="42" rx="9" fill="#ef4444"/><text x="133" y="29" text-anchor="middle" font-family="Arial" font-size="22" font-weight="900" fill="#ffffff">▶</text>
    <text x="178" y="31" font-family="Arial, sans-serif" font-size="32" font-weight="900" fill="#ffffff">@hardeepjethwani</text>
  </g>
  <g transform="translate(1218 638)" opacity="0.94">
    <rect x="0" y="0" width="326" height="150" rx="30" fill="#05070d" stroke="#ffffff" stroke-opacity="0.24" stroke-width="3"/>
    <image href="{KAPISTRA_LOCAL_NAME}" x="18" y="23" width="104" height="104" opacity="0.90"/>
    <text x="140" y="64" font-family="Arial, sans-serif" font-size="31" font-weight="900" fill="#ffffff">KAPISTRA</text>
    <text x="140" y="103" font-family="Arial, sans-serif" font-size="21" font-weight="800" fill="{accent_2}">Learn. Build. Lead.</text>
  </g>
  <rect x="0" y="0" width="1600" height="840" fill="none" stroke="{accent}" stroke-width="4" opacity="0.35"/>
</svg>
'''


def update_metadata(day_dir: Path) -> None:
    path = day_dir / "metadata.json"
    if not path.exists():
        return
    data = json.loads(path.read_text())
    assets = data.setdefault("assets", [])
    if "assets/cover.png" not in assets:
        assets.insert(0, "assets/cover.png")
    data["cover_image"] = "assets/cover.png"
    path.write_text(json.dumps(data, indent=2) + "\n")


def main() -> int:
    topics = json.loads(TOPICS_PATH.read_text())["topics"]
    for topic in topics:
        day = int(topic["day"])
        day_dir = ROOT / "blogs" / f"day-{day:02d}"
        assets_dir = day_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        if KAPISTRA_SOURCE.exists():
            shutil.copy2(KAPISTRA_SOURCE, assets_dir / KAPISTRA_LOCAL_NAME)
        (assets_dir / "cover.svg").write_text(svg_for(topic))
        update_metadata(day_dir)
    print(f"Generated {len(topics)} cover SVG files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
