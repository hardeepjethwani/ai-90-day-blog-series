#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOPICS_PATH = ROOT / "topics" / "topics.json"
KAPISTRA_ICON_SOURCE = ROOT / "brand" / "kapistra-icon-cutout.png"
KAPISTRA_NAME_SOURCE = ROOT / "brand" / "kapistra-name-transparent.png"
KAPISTRA_ICON_LOCAL_NAME = "kapistra-icon-cutout.png"
KAPISTRA_NAME_LOCAL_NAME = "kapistra-name-transparent.png"
COVER_WIDTH = 1600
COVER_HEIGHT = 840


PALETTES = [
    ("#ff2d55", "#ffd166", "#1b0611"),
    ("#38bdf8", "#a3ff12", "#03142b"),
    ("#ff7a18", "#facc15", "#1b0b02"),
    ("#a855f7", "#22d3ee", "#10051f"),
    ("#10b981", "#f9f871", "#02170f"),
    ("#f472b6", "#60a5fa", "#210617"),
]


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def wrap_title(text: str, max_chars: int = 24, max_lines: int = 5) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []

    for word in words:
        candidate = " ".join(current + [word])
        if current and len(candidate) > max_chars:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        lines.append(" ".join(current))

    if len(lines) <= max_lines:
        return lines

    kept = lines[: max_lines - 1]
    final = " ".join(lines[max_lines - 1 :])
    if len(final) > max_chars + 8:
        final = final[: max_chars + 5].rstrip() + "..."
    kept.append(final)
    return kept


def category_label(category: str) -> str:
    return category.upper().replace(" AND ", " & ")


def svg_for(topic: dict) -> str:
    day = int(topic["day"])
    title = topic["title"]
    category = topic["category"]
    accent, accent_2, deep = PALETTES[(day - 1) % len(PALETTES)]
    title_lines = wrap_title(title)
    font_size = 78 if len(title_lines) <= 2 else 66 if len(title_lines) == 3 else 56 if len(title_lines) == 4 else 50
    line_gap = 84 if len(title_lines) <= 2 else 70 if len(title_lines) == 3 else 60 if len(title_lines) == 4 else 54
    title_y = 286
    title_svg = "\n".join(
        f'<text x="110" y="{title_y + i * line_gap}" font-family="Arial Black, Arial, sans-serif" font-size="{font_size}" font-weight="900" fill="#ffffff">{esc(line)}</text>'
        for i, line in enumerate(title_lines)
    )
    underline_y = title_y + (len(title_lines) - 1) * line_gap + 34
    subtitle_y = underline_y + 78
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
  <rect width="1600" height="840" fill="#050816" opacity="0.22"/>
  <path d="M900 -80 C1190 90 1390 335 1625 620 L1625 840 L1165 840 C1085 650 1000 430 780 135 Z" fill="#111827" opacity="0.60"/>
  <path d="M1385 48 C1210 150 1080 308 1026 478" fill="none" stroke="url(#slash)" stroke-width="76" stroke-linecap="round" opacity="0.88"/>
  <path d="M1470 112 C1290 198 1175 342 1110 522" fill="none" stroke="#ffffff" stroke-width="20" stroke-linecap="round" opacity="0.40"/>
  <path d="M1115 90 L1530 270 L1365 620 L980 485 Z" fill="#ffffff" opacity="0.045"/>
  <g opacity="0.16">
    <rect x="875" y="224" width="155" height="48" rx="14" fill="#ffffff"/>
    <rect x="1040" y="324" width="175" height="48" rx="14" fill="#ffffff"/>
    <rect x="952" y="426" width="190" height="48" rx="14" fill="#ffffff"/>
    <rect x="1190" y="526" width="155" height="48" rx="14" fill="#ffffff"/>
  </g>
  <g opacity="0.22" stroke="{accent_2}" stroke-width="2">
    <path d="M72 248 H672"/>
    <path d="M72 654 H760"/>
    <path d="M96 228 V674"/>
    <path d="M714 228 V650"/>
  </g>
  <g filter="url(#textShadow)">
    <text x="110" y="105" font-family="Arial, sans-serif" font-size="38" font-style="italic" font-weight="800" fill="#ffffff">Learn with HJ</text>
    <rect x="108" y="138" width="285" height="54" rx="18" fill="{accent_2}" opacity="0.98"/>
    <text x="135" y="174" font-family="Arial, sans-serif" font-size="26" font-weight="900" fill="#050816">90 DAYS OF AI</text>
    <rect x="412" y="138" width="142" height="54" rx="18" fill="#ffffff" opacity="0.92"/>
    <text x="441" y="174" font-family="Arial, sans-serif" font-size="26" font-weight="900" fill="#050816">DAY {day:02d}</text>
    {title_svg}
  </g>
  <rect x="110" y="{underline_y}" width="520" height="10" rx="5" fill="{accent}"/>
  <rect x="110" y="{underline_y + 18}" width="285" height="10" rx="5" fill="{accent_2}"/>
  <g filter="url(#textShadow)">
    <rect x="110" y="{subtitle_y - 40}" width="540" height="64" rx="22" fill="#ffffff" opacity="0.12"/>
    <text x="140" y="{subtitle_y}" font-family="Arial, sans-serif" font-size="28" font-weight="900" fill="#ffffff">VISUAL GUIDE + EXAMPLES</text>
    <text x="110" y="{subtitle_y + 56}" font-family="Arial, sans-serif" font-size="27" font-weight="800" fill="{accent_2}">{esc(punch)}</text>
  </g>
  <g transform="translate(1068 612)" filter="url(#textShadow)">
    <rect x="0" y="0" width="310" height="70" rx="24" fill="#ffffff" opacity="0.13"/>
    <text x="28" y="44" font-family="Arial, sans-serif" font-size="24" font-weight="900" fill="#ffffff">signal &gt; hype</text>
  </g>
  <g transform="translate(110 720)">
    <rect x="0" y="0" width="42" height="42" rx="9" fill="#0a66c2"/><text x="21" y="29" text-anchor="middle" font-family="Arial" font-size="22" font-weight="900" fill="#ffffff">in</text>
    <rect x="56" y="0" width="42" height="42" rx="9" fill="#111111"/><text x="77" y="29" text-anchor="middle" font-family="Arial" font-size="22" font-weight="900" fill="#ffffff">X</text>
    <rect x="112" y="0" width="42" height="42" rx="9" fill="#ef4444"/><text x="133" y="29" text-anchor="middle" font-family="Arial" font-size="22" font-weight="900" fill="#ffffff">▶</text>
    <text x="178" y="31" font-family="Arial, sans-serif" font-size="32" font-weight="900" fill="#ffffff">@hardeepjethwani</text>
  </g>
  <g transform="translate(1272 720)" opacity="0.82">
    <image href="{KAPISTRA_ICON_LOCAL_NAME}" x="0" y="0" width="58" height="54" preserveAspectRatio="xMidYMid meet"/>
    <image href="{KAPISTRA_NAME_LOCAL_NAME}" x="71" y="8" width="205" height="38" preserveAspectRatio="xMidYMid meet"/>
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


def render_png(svg_path: Path, png_path: Path) -> None:
    rsvg = shutil.which("rsvg-convert") or "/opt/homebrew/bin/rsvg-convert"
    if not Path(rsvg).exists():
        raise RuntimeError("rsvg-convert is required to render cover PNG files.")
    subprocess.run(
        [rsvg, "-w", str(COVER_WIDTH), "-h", str(COVER_HEIGHT), str(svg_path), "-o", str(png_path)],
        check=True,
    )


def main() -> int:
    topics = json.loads(TOPICS_PATH.read_text())["topics"]
    for topic in topics:
        day = int(topic["day"])
        day_dir = ROOT / "blogs" / f"day-{day:02d}"
        assets_dir = day_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        for source, local_name in (
            (KAPISTRA_ICON_SOURCE, KAPISTRA_ICON_LOCAL_NAME),
            (KAPISTRA_NAME_SOURCE, KAPISTRA_NAME_LOCAL_NAME),
        ):
            if source.exists():
                shutil.copy2(source, assets_dir / local_name)
        cover_svg = assets_dir / "cover.svg"
        cover_svg.write_text(svg_for(topic))
        render_png(cover_svg, assets_dir / "cover.png")
        update_metadata(day_dir)
    print(f"Generated {len(topics)} cover SVG and PNG files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
