#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
TOPICS_PATH = ROOT / "topics" / "topics.json"
COVER_WIDTH = 1600
COVER_HEIGHT = 840
INLINE_WIDTH = 1400
INLINE_HEIGHT = 788
FLOW_WIDTH = 1200
FLOW_HEIGHT = 675

sys.path.insert(0, str(SCRIPTS_DIR))

from generate_hashnode_covers import main as generate_covers  # noqa: E402
from generate_remaining_blogs import flow_svg, hero_svg, safe_title  # noqa: E402


def rsvg_path() -> str:
    rsvg = shutil.which("rsvg-convert") or "/opt/homebrew/bin/rsvg-convert"
    if not Path(rsvg).exists():
        raise RuntimeError("rsvg-convert is required to render PNG files.")
    return rsvg


def render(svg_path: Path, png_path: Path, width: int, height: int) -> None:
    subprocess.run(
        [rsvg_path(), "-w", str(width), "-h", str(height), str(svg_path), "-o", str(png_path)],
        check=True,
    )


def regenerate_inline_visuals() -> int:
    topics = json.loads(TOPICS_PATH.read_text())["topics"]
    count = 0

    for topic in topics:
        day = int(topic["day"])
        if day == 1:
            continue

        topic = {**topic, "title": safe_title(topic["title"])}
        assets_dir = ROOT / "blogs" / f"day-{day:02d}" / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        hero_svg_path = assets_dir / "hero.svg"
        flow_svg_path = assets_dir / "concept-flow.svg"
        hero_svg_path.write_text(hero_svg(topic), encoding="utf-8")
        flow_svg_path.write_text(flow_svg(topic), encoding="utf-8")

        render(hero_svg_path, assets_dir / "hero.png", INLINE_WIDTH, INLINE_HEIGHT)
        render(flow_svg_path, assets_dir / "concept-flow.png", FLOW_WIDTH, FLOW_HEIGHT)
        count += 2

    return count


def render_day_one_existing_svgs() -> int:
    assets_dir = ROOT / "blogs" / "day-01" / "assets"
    rendered = 0
    sizes = {
        "hero-llm-builder.svg": (INLINE_WIDTH, INLINE_HEIGHT),
        "tokenization-flow.svg": (FLOW_WIDTH, FLOW_HEIGHT),
        "next-token-loop.svg": (FLOW_WIDTH, FLOW_HEIGHT),
        "training-vs-inference.svg": (FLOW_WIDTH, FLOW_HEIGHT),
        "practical-llm-system.svg": (FLOW_WIDTH, FLOW_HEIGHT),
    }

    for name, (width, height) in sizes.items():
        svg_path = assets_dir / name
        if not svg_path.exists():
            continue
        render(svg_path, svg_path.with_suffix(".png"), width, height)
        rendered += 1

    return rendered


def main() -> int:
    generate_covers()
    inline_count = regenerate_inline_visuals()
    day_one_count = render_day_one_existing_svgs()
    print(f"Regenerated {inline_count} generated inline images and {day_one_count} Day 01 images.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
