#!/usr/bin/env python3
"""Validate dataset integrity, taxonomy coverage, and static site assets."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"

REQUIRED_FIELDS = (
    "id",
    "title",
    "authors",
    "journal",
    "journal_slug",
    "family",
    "tier",
    "year",
    "discipline",
    "pattern",
    "figure_label",
    "doi",
    "license",
    "image",
    "highres",
    "paper",
    "palette",
    "w",
    "h",
)

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def main() -> int:
    errors: list[str] = []

    required_files = [
        ROOT_DIR / "index.html",
        ROOT_DIR / "README.md",
        ROOT_DIR / "LICENSE",
        ROOT_DIR / ".nojekyll",
        ASSETS_DIR / "style.css",
        ASSETS_DIR / "i18n.js",
        ASSETS_DIR / "app.js",
        ASSETS_DIR / "figures.js",
        DATA_DIR / "journals.json",
        DATA_DIR / "figures.json",
    ]
    for path in required_files:
        if not path.exists() or (path.name != ".nojekyll" and path.stat().st_size == 0):
            errors.append(f"Missing or empty required file: {path}")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1

    journals_cfg = json.loads((DATA_DIR / "journals.json").read_text(encoding="utf-8"))
    payload = json.loads((DATA_DIR / "figures.json").read_text(encoding="utf-8"))
    figures = payload.get("figures", [])

    valid_families = {x["id"] for x in journals_cfg["families"]}
    valid_tiers = {x["id"] for x in journals_cfg["tiers"]}
    valid_disciplines = {x["id"] for x in journals_cfg["disciplines"]}
    valid_patterns = {x["id"] for x in journals_cfg["patterns"]}

    if len(figures) < 3000:
        errors.append(f"Expected >= 3000 figures in gallery, got {len(figures)}")

    seen_ids: set[str] = set()
    family_counts: Counter[str] = Counter()
    tier_counts: Counter[str] = Counter()
    year_counts: Counter[int] = Counter()
    disc_counts: Counter[str] = Counter()
    pat_counts: Counter[str] = Counter()

    for idx, fig in enumerate(figures):
        for field in REQUIRED_FIELDS:
            if field not in fig or fig[field] in (None, ""):
                errors.append(f"Item #{idx} ({fig.get('id')}) missing field '{field}'")

        fid = fig.get("id", "")
        if fid in seen_ids:
            errors.append(f"Duplicate figure id: {fid}")
        seen_ids.add(fid)

        if fig.get("family") not in valid_families:
            errors.append(f"{fid}: invalid family {fig.get('family')}")
        if fig.get("tier") not in valid_tiers:
            errors.append(f"{fid}: invalid tier {fig.get('tier')}")
        if fig.get("discipline") not in valid_disciplines:
            errors.append(f"{fid}: invalid discipline {fig.get('discipline')}")
        if fig.get("pattern") not in valid_patterns:
            errors.append(f"{fid}: invalid pattern {fig.get('pattern')}")
        if fig.get("year") not in (2024, 2025, 2026):
            errors.append(f"{fid}: year out of 2024-2026 range: {fig.get('year')}")
        if not str(fig.get("image", "")).startswith("https://"):
            errors.append(f"{fid}: invalid image URL {fig.get('image')}")
        if not isinstance(fig.get("w"), int) or fig["w"] <= 0 or not isinstance(fig.get("h"), int) or fig["h"] <= 0:
            errors.append(f"{fid}: invalid dimensions {fig.get('w')}x{fig.get('h')}")

        pal = fig.get("palette", [])
        if not isinstance(pal, list) or len(pal) < 5 or not all(isinstance(c, str) and HEX_RE.match(c) for c in pal):
            errors.append(f"{fid}: invalid palette {pal}")

        family_counts[fig.get("family", "")] += 1
        tier_counts[fig.get("tier", "")] += 1
        year_counts[int(fig.get("year", 0))] += 1
        disc_counts[fig.get("discipline", "")] += 1
        pat_counts[fig.get("pattern", "")] += 1

    # Check coverage across dimensions
    for fam in valid_families:
        if family_counts[fam] == 0:
            errors.append(f"Zero figures found for family '{fam}'")
    for tier in valid_tiers:
        if tier_counts[tier] == 0:
            errors.append(f"Zero figures found for tier '{tier}'")
    for yr in (2024, 2025, 2026):
        if year_counts[yr] == 0:
            errors.append(f"Zero figures found for year {yr}")
    for disc in valid_disciplines:
        if disc_counts[disc] == 0:
            errors.append(f"Zero figures found for discipline '{disc}'")

    # Verify assets/figures.js matches figures.json count
    js_text = (ASSETS_DIR / "figures.js").read_text(encoding="utf-8")
    if "window.FIGURES =" not in js_text or "window.GALLERY_META =" not in js_text:
        errors.append("assets/figures.js missing window.FIGURES or window.GALLERY_META")

    print("=== Gallery Validation Summary ===")
    print(f"Total figures : {len(figures)}")
    print(f"Families      : {dict(family_counts)}")
    print(f"Tiers         : {dict(tier_counts)}")
    print(f"Years         : {dict(year_counts)}")
    print(f"Disciplines   : {dict(disc_counts)}")
    print(f"Patterns      : {dict(pat_counts)}")

    if errors:
        print(f"\nFAILED with {len(errors)} error(s):")
        for e in errors[:20]:
            print(" -", e)
        return 1

    print("\nVALIDATION PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
