#!/usr/bin/env python3
"""Build static Agent API v1 JSON files and sync assets/figures.js from data/figures.json."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import quote

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "figures.json"
FIGURES_JS_PATH = ROOT_DIR / "assets" / "figures.js"
API_V1_DIR = ROOT_DIR / "api" / "v1"
DEFAULT_BASE_URL = "https://daydayup-xq.github.io/cns-paper-figure-gallery"
SCHEMA_VERSION = "1.0"

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
JOURNAL_ORDER = {"Nature": 0, "Science": 1, "Cell": 2}


def normalize_hex(value: Any, ctx: str) -> str:
    if not isinstance(value, str) or not HEX_RE.match(value.strip()):
        raise ValueError(f"{ctx}: invalid HEX color {value!r}")
    return value.strip().upper()


def validate_curated_entry(fig: dict[str, Any]) -> dict[str, Any]:
    fid = fig.get("id")
    if not isinstance(fid, str) or not fid.strip():
        raise ValueError("Figure missing valid 'id'")

    for field in ("title", "journal", "tier", "discipline", "pattern", "paper"):
        if not isinstance(fig.get(field), str) or not fig[field].strip():
            raise ValueError(f"{fid}: missing or empty '{field}'")
    if not isinstance(fig.get("year"), int):
        raise ValueError(f"{fid}: invalid integer 'year': {fig.get('year')!r}")

    image_hd = fig.get("highres") or fig.get("image")
    if not isinstance(image_hd, str) or not image_hd.startswith("https://"):
        raise ValueError(f"{fid}: invalid image_hd URL {image_hd!r}")
    if not fig["paper"].startswith("https://"):
        raise ValueError(f"{fid}: invalid doi URL {fig['paper']!r}")

    pc = fig.get("palette_curated")
    if not isinstance(pc, dict) or pc.get("status") != "verified":
        raise ValueError(f"{fid}: palette_curated.status must be 'verified'")

    roles = pc.get("roles")
    if not isinstance(roles, dict):
        raise ValueError(f"{fid}: palette_curated.roles must be an object")

    raw_primary = roles.get("primary")
    if not isinstance(raw_primary, list) or not (3 <= len(raw_primary) <= 6):
        raise ValueError(f"{fid}: roles.primary must contain 3-6 HEX colors")
    primary = [normalize_hex(c, f"{fid}.roles.primary[{i}]") for i, c in enumerate(raw_primary)]
    accent = normalize_hex(roles.get("accent"), f"{fid}.roles.accent")
    neutral = normalize_hex(roles.get("neutral"), f"{fid}.roles.neutral")
    background = normalize_hex(roles.get("background"), f"{fid}.roles.background")

    cb_safe = pc.get("colorblind_safe")
    if not isinstance(cb_safe, bool):
        raise ValueError(f"{fid}: colorblind_safe must be a boolean")

    layout_notes = pc.get("layout_notes")
    if not isinstance(layout_notes, str) or not layout_notes.strip():
        raise ValueError(f"{fid}: layout_notes must be a non-empty string")

    verified_by = pc.get("verified_by")
    if not isinstance(verified_by, str) or not verified_by.strip():
        raise ValueError(f"{fid}: verified_by must be a non-empty string")

    return {
        "primary": primary,
        "accent": accent,
        "neutral": neutral,
        "background": background,
        "colorblind_safe": cb_safe,
        "layout_notes": layout_notes.strip(),
        "verified_by": verified_by.strip(),
    }


def resolve_pmc_link(fig: dict[str, Any]) -> str | None:
    pmc_url = (fig.get("pmc_url") or "").strip()
    if pmc_url:
        if not pmc_url.startswith("https://"):
            raise ValueError(f"{fig['id']}: invalid pmc_url {pmc_url!r}")
        return pmc_url
    pmcid = (fig.get("pmcid") or "").strip()
    if pmcid:
        return f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    return None


def build_item_payload(fig: dict[str, Any], clean_pc: dict[str, Any], base_url: str) -> dict[str, Any]:
    fid = fig["id"]
    encoded_id = quote(fid, safe="")
    return {
        "schema_version": SCHEMA_VERSION,
        "id": fid,
        "meta": {
            "title": fig["title"],
            "journal": fig["journal"],
            "journal_tier": fig["tier"],
            "year": int(fig["year"]),
            "discipline": fig["discipline"],
            "figure_type": fig["pattern"],
        },
        "links": {
            "gallery_page": f"{base_url}/#fig={encoded_id}",
            "image_hd": fig.get("highres") or fig["image"],
            "doi": fig["paper"],
            "pmc": resolve_pmc_link(fig),
        },
        "palette": {
            "roles": {
                "primary": clean_pc["primary"],
                "accent": clean_pc["accent"],
                "neutral": clean_pc["neutral"],
                "background": clean_pc["background"],
            },
            "colorblind_safe": clean_pc["colorblind_safe"],
        },
        "reference": {
            "layout_notes": clean_pc["layout_notes"],
        },
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build static Agent API v1 JSON files from data/figures.json")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Deployed GitHub Pages base URL")
    parser.add_argument("--output-dir", type=Path, default=API_V1_DIR, help="Output directory for /api/v1")
    parser.add_argument("--no-sync-js", action="store_true", help="Skip regenerating assets/figures.js")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    out_dir: Path = args.output_dir
    items_dir = out_dir / "items"

    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    meta = payload.get("meta") or {}
    figures = payload.get("figures") or []

    verified_figs = [
        fig
        for fig in figures
        if isinstance(fig.get("palette_curated"), dict) and fig["palette_curated"].get("status") == "verified"
    ]
    verified_figs.sort(key=lambda f: (JOURNAL_ORDER.get(f.get("journal", ""), 99), -int(f.get("year", 0)), f.get("id", "")))

    full_items: list[dict[str, Any]] = []
    index_items: list[dict[str, Any]] = []
    for fig in verified_figs:
        clean_pc = validate_curated_entry(fig)
        item_obj = build_item_payload(fig, clean_pc, base_url)
        full_items.append(item_obj)
        encoded_id = quote(fig["id"], safe="")
        index_items.append(
            {
                "id": fig["id"],
                "journal": fig["journal"],
                "year": int(fig["year"]),
                "discipline": fig["discipline"],
                "figure_type": fig["pattern"],
                "item_api_url": f"{base_url}/api/v1/items/{encoded_id}.json",
                "primary_colors": clean_pc["primary"],
            }
        )

    updated_at = str(meta.get("updated_at") or "").strip() or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    items_dir.mkdir(parents=True, exist_ok=True)
    expected_filenames = {f"{item['id']}.json" for item in full_items}
    for existing in items_dir.glob("*.json"):
        if existing.name not in expected_filenames:
            existing.unlink()

    for item in full_items:
        write_json(items_dir / f"{item['id']}.json", item)

    write_json(
        out_dir / "index.json",
        {
            "schema_version": SCHEMA_VERSION,
            "updated_at": updated_at,
            "base_url": base_url,
            "count": len(index_items),
            "items": index_items,
        },
    )
    write_json(
        out_dir / "curated.json",
        {
            "schema_version": SCHEMA_VERSION,
            "updated_at": updated_at,
            "base_url": base_url,
            "count": len(full_items),
            "items": full_items,
        },
    )

    if not args.no_sync_js:
        FIGURES_JS_PATH.parent.mkdir(parents=True, exist_ok=True)
        FIGURES_JS_PATH.write_text(
            f"window.GALLERY_META = {json.dumps(meta, ensure_ascii=False)};\n"
            f"window.FIGURES = {json.dumps(figures, ensure_ascii=False)};\n",
            encoding="utf-8",
        )

    print(
        f"Built static Agent API v1 in {out_dir} "
        f"({len(full_items)} curated items; figures.js synced={not args.no_sync_js})."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
