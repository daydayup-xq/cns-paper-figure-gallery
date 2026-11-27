#!/usr/bin/env python3
"""Validate dataset integrity, taxonomy coverage, and static site assets."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
API_V1_DIR = ROOT_DIR / "api" / "v1"

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
    curated_ids: list[str] = []
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
        cur_yr = datetime.now(timezone.utc).year
        if not isinstance(fig.get("year"), int) or not (2024 <= fig["year"] <= cur_yr):
            errors.append(f"{fid}: year out of 2024-{cur_yr} range: {fig.get('year')}")
        if not str(fig.get("image", "")).startswith("https://"):
            errors.append(f"{fid}: invalid image URL {fig.get('image')}")
        if not isinstance(fig.get("w"), int) or fig["w"] <= 0 or not isinstance(fig.get("h"), int) or fig["h"] <= 0:
            errors.append(f"{fid}: invalid dimensions {fig.get('w')}x{fig.get('h')}")

        pal = fig.get("palette", [])
        if not isinstance(pal, list) or len(pal) < 5 or not all(isinstance(c, str) and HEX_RE.match(c) for c in pal):
            errors.append(f"{fid}: invalid palette {pal}")

        pc = fig.get("palette_curated")
        if pc is not None:
            if not isinstance(pc, dict):
                errors.append(f"{fid}: palette_curated must be an object")
            elif pc.get("status") == "verified":
                curated_ids.append(fid)
                roles = pc.get("roles")
                if not isinstance(roles, dict):
                    errors.append(f"{fid}: palette_curated.roles missing")
                else:
                    prim = roles.get("primary")
                    if not isinstance(prim, list) or not (3 <= len(prim) <= 6) or not all(isinstance(c, str) and HEX_RE.match(c) for c in prim):
                        errors.append(f"{fid}: palette_curated.roles.primary must have 3-6 HEX colors")
                    for role_key in ("accent", "neutral", "background"):
                        if not isinstance(roles.get(role_key), str) or not HEX_RE.match(roles[role_key]):
                            errors.append(f"{fid}: palette_curated.roles.{role_key} invalid HEX {roles.get(role_key)!r}")
                if not isinstance(pc.get("colorblind_safe"), bool):
                    errors.append(f"{fid}: palette_curated.colorblind_safe must be bool")
                if not isinstance(pc.get("layout_notes"), str) or not pc["layout_notes"].strip():
                    errors.append(f"{fid}: palette_curated.layout_notes must be non-empty string")
                if not isinstance(pc.get("verified_by"), str) or not pc["verified_by"].strip():
                    errors.append(f"{fid}: palette_curated.verified_by must be non-empty string")

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

    # Verify static Agent API v1 artifacts match verified palette_curated entries
    idx_path = API_V1_DIR / "index.json"
    cur_path = API_V1_DIR / "curated.json"
    items_dir = API_V1_DIR / "items"
    if not idx_path.exists() or not cur_path.exists() or not items_dir.is_dir():
        errors.append("Missing static Agent API files under api/v1/")
    else:
        try:
            idx_data = json.loads(idx_path.read_text(encoding="utf-8"))
            cur_data = json.loads(cur_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"Invalid JSON in api/v1: {exc}")
            idx_data, cur_data = {}, {}

        expected_set = set(curated_ids)
        for label, obj in (("api/v1/index.json", idx_data), ("api/v1/curated.json", cur_data)):
            if obj.get("schema_version") != "1.0":
                errors.append(f"{label}: schema_version must be '1.0'")
            if obj.get("count") != len(expected_set):
                errors.append(f"{label}: count={obj.get('count')} != expected {len(expected_set)}")
            if not isinstance(obj.get("items"), list) or len(obj["items"]) != len(expected_set):
                errors.append(f"{label}: items length mismatch")
            if not str(obj.get("base_url", "")).startswith("https://"):
                errors.append(f"{label}: invalid base_url {obj.get('base_url')!r}")
            if not str(obj.get("updated_at", "")).strip():
                errors.append(f"{label}: empty updated_at")

        if isinstance(idx_data.get("items"), list):
            for it in idx_data["items"]:
                if it.get("id") not in expected_set:
                    errors.append(f"api/v1/index.json unexpected id {it.get('id')}")
                if not str(it.get("item_api_url", "")).startswith("https://"):
                    errors.append(f"api/v1/index.json invalid item_api_url for {it.get('id')}")
                pcols = it.get("primary_colors") or []
                if not (3 <= len(pcols) <= 6) or not all(isinstance(c, str) and HEX_RE.match(c) for c in pcols):
                    errors.append(f"api/v1/index.json invalid primary_colors for {it.get('id')}")

        cur_by_id: dict[str, dict] = {}
        if isinstance(cur_data.get("items"), list):
            for it in cur_data["items"]:
                cid = it.get("id", "")
                cur_by_id[cid] = it
                links = it.get("links") or {}
                for lk in ("gallery_page", "image_hd", "doi"):
                    if not str(links.get(lk, "")).startswith("https://"):
                        errors.append(f"api/v1/curated.json {cid}: invalid links.{lk}={links.get(lk)!r}")
                if links.get("pmc") is not None and not str(links["pmc"]).startswith("https://"):
                    errors.append(f"api/v1/curated.json {cid}: invalid links.pmc={links.get('pmc')!r}")
                if not str(((it.get("reference") or {}).get("layout_notes") or "")).strip():
                    errors.append(f"api/v1/curated.json {cid}: empty reference.layout_notes")

        actual_item_files = {p.name for p in items_dir.glob("*.json")}
        expected_item_files = {f"{cid}.json" for cid in expected_set}
        if actual_item_files != expected_item_files:
            errors.append(f"api/v1/items/*.json mismatch: expected {sorted(expected_item_files)}, got {sorted(actual_item_files)}")
        for cid in expected_set:
            ip = items_dir / f"{cid}.json"
            if ip.exists():
                item_payload = json.loads(ip.read_text(encoding="utf-8"))
                if item_payload != cur_by_id.get(cid):
                    errors.append(f"api/v1/items/{cid}.json differs from api/v1/curated.json entry")

    print("=== Gallery Validation Summary ===")
    print(f"Total figures : {len(figures)}")
    print(f"Curated API   : {len(curated_ids)} verified items")
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
