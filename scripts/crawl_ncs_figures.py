#!/usr/bin/env python3
"""Crawl Open Access (2024-2026) main figures from Nature, Science, and Cell journals.

Uses only official APIs and publisher/PMC CDNs (no HTML scraping behind CAPTCHAs):
  - Discovery: OpenAlex Works API (open_access.is_oa=true, publication_year=2024-2026, has_pmcid=true)
  - Nature Portfolio (10.1038/...): deterministic Springer Nature CDN + NCBI PMC OAI-PMH captions
  - Cell Press (10.1016/j.*): Crossref/OAI PII -> Elsevier ars.els-cdn.com + Europe PMC XML fallback
  - Science Family (10.1126/*) & fallback: Europe PMC fullTextXML <?cloudpmc-path?> -> cdn.ncbi.nlm.nih.gov
  - Image metadata: authentic pixel width/height & 5-color scientific HEX palette extraction
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import threading
import time
from typing import Any
from urllib.parse import quote
import xml.etree.ElementTree as ET
import zlib

import requests

try:
    from PIL import Image as PILImage  # type: ignore
except ImportError:
    PILImage = None

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
JOURNALS_PATH = DATA_DIR / "journals.json"
FIGURES_JSON_PATH = DATA_DIR / "figures.json"
FIGURES_JS_PATH = ASSETS_DIR / "figures.js"

USER_AGENT = "NCSPaperFigureGallery/1.0 (https://github.com/ncs-paper-figure-gallery; mailto:ncsgallery@users.noreply.github.com)"

OPENALEX_FIELD_TO_DISCIPLINE: dict[str, str] = {
    "Biochemistry, Genetics and Molecular Biology": "bio-med",
    "Medicine": "bio-med",
    "Immunology and Microbiology": "bio-med",
    "Neuroscience": "bio-med",
    "Pharmacology, Toxicology and Pharmaceutics": "bio-med",
    "Agricultural and Biological Sciences": "bio-med",
    "Health Professions": "bio-med",
    "Nursing": "bio-med",
    "Dentistry": "bio-med",
    "Veterinary": "bio-med",
    "Chemistry": "mat-chem",
    "Materials Science": "mat-chem",
    "Chemical Engineering": "mat-chem",
    "Energy": "energy-env",
    "Environmental Science": "energy-env",
    "Earth and Planetary Sciences": "energy-env",
    "Physics and Astronomy": "phys-eng",
    "Engineering": "phys-eng",
    "Computer Science": "ai-comp",
    "Mathematics": "ai-comp",
    "Decision Sciences": "ai-comp",
    "Social Sciences": "inter-soc",
    "Psychology": "inter-soc",
    "Economics, Econometrics and Finance": "inter-soc",
    "Arts and Humanities": "inter-soc",
    "Business, Management and Accounting": "inter-soc",
    "Multidisciplinary": "inter-soc",
}

DISCIPLINE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ai-comp": (
        "deep learning",
        "neural network",
        "foundation model",
        "large language model",
        "transformer",
        "machine learning",
        "artificial intelligence",
        "reinforcement learning",
        "diffusion model",
        "computational framework",
        "algorithm",
        "bioinformatics",
        "alphafold",
        "graph neural",
        "benchmark",
    ),
    "energy-env": (
        "battery",
        "lithium",
        "sodium-ion",
        "perovskite solar",
        "photovoltaic",
        "electrocataly",
        "hydrogen evolution",
        "co2 reduction",
        "carbon capture",
        "climate",
        "warming",
        "ecosystem",
        "glacier",
        "ocean",
        "earthquake",
        "geophys",
        "biodiversity",
        "decarboniz",
        "fuel cell",
        "supercapacitor",
    ),
    "mat-chem": (
        "nanoparticle",
        "metal-organic framework",
        "mof",
        "covalent organic",
        "polymer",
        "synthesis",
        "catalysis",
        "catalyst",
        "crystal",
        "2d material",
        "graphene",
        "mxene",
        "hydrogel",
        "supramolecular",
        "self-assembly",
        "ligand",
        "alloy",
        "nanowire",
        "chemical",
    ),
    "phys-eng": (
        "quantum",
        "qubit",
        "photonic",
        "laser",
        "metasurface",
        "metamaterial",
        "superconduct",
        "semiconductor",
        "transistor",
        "optoelectronic",
        "bose-einstein",
        "optical",
        "waveguide",
        "terahertz",
        "robot",
        "actuator",
        "microfluidic",
        "sensor",
        "neuromorphic",
    ),
    "inter-soc": (
        "policy",
        "economic",
        "misinformation",
        "social network",
        "human behaviour",
        "human behavior",
        "inequality",
        "urban",
        "governance",
        "survey",
        "education",
        "sustainability transition",
        "global",
        "decision-making",
    ),
    "bio-med": (
        "cell",
        "protein",
        "tumor",
        "tumour",
        "cancer",
        "immune",
        "neuron",
        "brain",
        "gene",
        "genomic",
        "crispr",
        "mrna",
        "clinical",
        "patient",
        "mouse",
        "mice",
        "single-cell",
        "cryo-em",
        "organoid",
        "therapeutic",
        "antibody",
        "vaccine",
    ),
}

NATURE_DOI_RE = re.compile(r"^10\.1038/s(\d{5})-(\d{3})-(\d+)-[0-9A-Za-z]+$")
_THREAD_LOCAL = threading.local()


def make_session() -> requests.Session:
    sess = getattr(_THREAD_LOCAL, "session", None)
    if sess is None:
        sess = requests.Session()
        sess.headers.update({"User-Agent": USER_AGENT})
        adapter = requests.adapters.HTTPAdapter(pool_connections=32, pool_maxsize=32)
        sess.mount("https://", adapter)
        sess.mount("http://", adapter)
        _THREAD_LOCAL.session = sess
    return sess


def reconstruct_abstract(inv: dict[str, list[int]] | None) -> str:
    if not inv:
        return ""
    pairs: list[tuple[int, str]] = []
    for word, positions in inv.items():
        for pos in positions:
            pairs.append((pos, word))
    pairs.sort(key=lambda x: x[0])
    return " ".join(w for _, w in pairs)


def classify_discipline(
    journal: dict[str, Any],
    work: dict[str, Any],
    abstract: str,
    caption: str,
) -> str:
    default_disc = journal.get("default_discipline", "bio-med")
    if not journal.get("multidisciplinary", False):
        return default_disc

    topic = work.get("primary_topic") or {}
    field_name = (topic.get("field") or {}).get("display_name") or ""
    domain_name = (topic.get("domain") or {}).get("display_name") or ""
    text = f"{work.get('title', '')} {abstract} {caption}".lower()

    # Check specific keyword overrides first for multidisciplinary papers
    scores: dict[str, int] = {k: 0 for k in DISCIPLINE_KEYWORDS}
    for disc, kws in DISCIPLINE_KEYWORDS.items():
        for kw in kws:
            if kw in text:
                scores[disc] += 2 if kw in (work.get("title") or "").lower() else 1

    mapped = OPENALEX_FIELD_TO_DISCIPLINE.get(field_name)
    if mapped:
        scores[mapped] += 3
    elif domain_name == "Physical Sciences":
        scores["phys-eng"] += 1
    elif domain_name == "Social Sciences":
        scores["inter-soc"] += 1

    best_disc = max(scores.items(), key=lambda kv: kv[1])
    if best_disc[1] > 0:
        return best_disc[0]
    return mapped or default_disc


def classify_pattern(fig_label: str, caption: str, title: str, is_ga: bool) -> str:
    if is_ga:
        return "graphical-abstract"
    txt = f"{fig_label} {caption} {title}".lower()
    if any(k in txt for k in ("graphical abstract", "visual summary", "overview schematic")):
        return "graphical-abstract"
    if any(
        k in txt
        for k in (
            "workflow",
            "pipeline",
            "architecture",
            "framework",
            "protocol",
            "flowchart",
            "training",
            "model overview",
            "experimental design",
            "study design",
        )
    ):
        return "pipeline"
    if any(
        k in txt
        for k in (
            "mechanism",
            "pathway",
            "signaling",
            "signalling",
            "catalytic cycle",
            "schematic of",
            "schematic illustration",
            "proposed mechanism",
            "working model",
        )
    ):
        return "mechanism"
    if any(
        k in txt
        for k in (
            "cryo-em",
            "crystal structure",
            "spatial",
            "umap",
            "atlas",
            "tomography",
            "microscopy",
            "tem ",
            "sem ",
            "afm ",
            "global map",
            "distribution map",
        )
    ):
        return "characterization"
    # Multi-panel check: labels like a, b, c, d or (A) (B) (C)
    if re.search(r"(\bb\b.*\bc\b|\(b\).*\(c\)|panels?\s+a)", txt):
        return "multipanel"
    return "multipanel"


def clean_text(raw: str) -> str:
    txt = re.sub(r"<[^>]+>", " ", raw or "")
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def parse_png_info(data: bytes) -> tuple[int, int]:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return 0, 0
    w, h = struct.unpack(">II", data[16:24])
    return int(w), int(h)


def parse_jpeg_info(data: bytes) -> tuple[int, int]:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return 0, 0
    i = 2
    n = len(data)
    while i < n - 8:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xD8, 0xD9, 0x00) or (0xD0 <= marker <= 0xD7):
            i += 2
            continue
        if i + 4 > n:
            break
        seg_len = struct.unpack(">H", data[i + 2 : i + 4])[0]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            if i + 9 <= n:
                h, w = struct.unpack(">HH", data[i + 5 : i + 9])
                return int(w), int(h)
        i += 2 + max(seg_len, 2)
    return 0, 0


def parse_webp_info(data: bytes) -> tuple[int, int]:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return 0, 0
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        w = 1 + int.from_bytes(data[24:27], "little")
        h = 1 + int.from_bytes(data[27:30], "little")
        return w, h
    if chunk == b"VP8 " and len(data) >= 30:
        w = struct.unpack("<H", data[26:28])[0] & 0x3FFF
        h = struct.unpack("<H", data[28:30])[0] & 0x3FFF
        return w, h
    if chunk == b"VP8L" and len(data) >= 25:
        b0, b1, b2, b3 = data[21:25]
        bits = b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
        w = (bits & 0x3FFF) + 1
        h = ((bits >> 14) & 0x3FFF) + 1
        return w, h
    return 0, 0


def get_image_dimensions_pure(data: bytes) -> tuple[int, int]:
    w, h = parse_png_info(data)
    if w > 0 and h > 0:
        return w, h
    w, h = parse_jpeg_info(data)
    if w > 0 and h > 0:
        return w, h
    return parse_webp_info(data)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def color_distance_sq(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> int:
    return (c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2


def select_distinct_palette(rgb_samples: list[tuple[int, int, int]], count: int = 5) -> list[str]:
    buckets: dict[tuple[int, int, int], list[tuple[int, int, int]]] = {}
    for r, g, b in rgb_samples:
        mx, mn = max(r, g, b), min(r, g, b)
        # Skip near-white backgrounds, near-black axes/text, and neutral grays
        if mx > 242 and mn > 230:
            continue
        if mx < 28:
            continue
        if (mx - mn) < 18 and (mx > 190 or mn < 60):
            continue
        q = (r >> 4, g >> 4, b >> 4)
        buckets.setdefault(q, []).append((r, g, b))

    ranked = sorted(buckets.values(), key=len, reverse=True)
    chosen: list[tuple[int, int, int]] = []
    for pts in ranked:
        n = len(pts)
        avg = (
            sum(p[0] for p in pts) // n,
            sum(p[1] for p in pts) // n,
            sum(p[2] for p in pts) // n,
        )
        if all(color_distance_sq(avg, prev) > 2200 for prev in chosen):
            chosen.append(avg)
            if len(chosen) >= count:
                break

    if len(chosen) < count:
        for pts in ranked:
            n = len(pts)
            avg = (
                sum(p[0] for p in pts) // n,
                sum(p[1] for p in pts) // n,
                sum(p[2] for p in pts) // n,
            )
            if all(color_distance_sq(avg, prev) > 650 for prev in chosen):
                chosen.append(avg)
                if len(chosen) >= count:
                    break

    defaults = [(43, 92, 143), (200, 75, 49), (46, 139, 87), (217, 140, 38), (114, 78, 152)]
    for d in defaults:
        if len(chosen) >= count:
            break
        if all(color_distance_sq(d, prev) > 900 for prev in chosen):
            chosen.append(d)

    return [rgb_to_hex(*c) for c in chosen[:count]]


def extract_png_samples_pure(data: bytes, max_samples: int = 3500) -> tuple[int, int, list[tuple[int, int, int]]]:
    """Decode PNG scanlines in pure Python (for 8-bit RGB/RGBA/Palette PNGs)."""
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return 0, 0, []
    pos = 8
    w = h = bit_depth = color_type = interlace = 0
    palette: list[tuple[int, int, int]] = []
    idat = bytearray()
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        ctype = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if ctype == b"IHDR" and len(chunk_data) >= 13:
            w, h, bit_depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", chunk_data[:13])
        elif ctype == b"PLTE":
            for i in range(0, len(chunk_data) - 2, 3):
                palette.append((chunk_data[i], chunk_data[i + 1], chunk_data[i + 2]))
        elif ctype == b"IDAT":
            idat.extend(chunk_data)
        elif ctype == b"IEND":
            break

    if w <= 0 or h <= 0 or bit_depth != 8 or interlace != 0 or color_type not in (2, 3, 6):
        return w, h, []

    bpp = {2: 3, 3: 1, 6: 4}[color_type]
    stride = w * bpp
    try:
        raw = zlib.decompress(bytes(idat))
    except Exception:
        return w, h, []

    if len(raw) < h * (stride + 1):
        return w, h, []

    row_step = max(1, h // 60)
    col_step = max(1, w // 60)
    samples: list[tuple[int, int, int]] = []
    prev_row = bytearray(stride)

    def paeth(a: int, b: int, c: int) -> int:
        p = a + b - c
        pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
        if pa <= pb and pa <= pc:
            return a
        return b if pb <= pc else c

    for y in range(h):
        row_start = y * (stride + 1)
        flt = raw[row_start]
        scan = bytearray(raw[row_start + 1 : row_start + 1 + stride])
        if flt == 1:
            for x in range(bpp, stride):
                scan[x] = (scan[x] + scan[x - bpp]) & 0xFF
        elif flt == 2:
            for x in range(stride):
                scan[x] = (scan[x] + prev_row[x]) & 0xFF
        elif flt == 3:
            for x in range(stride):
                left = scan[x - bpp] if x >= bpp else 0
                scan[x] = (scan[x] + ((left + prev_row[x]) >> 1)) & 0xFF
        elif flt == 4:
            for x in range(stride):
                left = scan[x - bpp] if x >= bpp else 0
                up = prev_row[x]
                up_left = prev_row[x - bpp] if x >= bpp else 0
                scan[x] = (scan[x] + paeth(left, up, up_left)) & 0xFF
        prev_row = scan

        if y % row_step == 0:
            for x in range(0, w, col_step):
                idx = x * bpp
                if color_type == 2:
                    samples.append((scan[idx], scan[idx + 1], scan[idx + 2]))
                elif color_type == 6:
                    if scan[idx + 3] > 128:
                        samples.append((scan[idx], scan[idx + 1], scan[idx + 2]))
                elif color_type == 3:
                    pidx = scan[idx]
                    if pidx < len(palette):
                        samples.append(palette[pidx])
                if len(samples) >= max_samples:
                    return w, h, samples
    return w, h, samples


def extract_with_pil(data: bytes) -> tuple[int, int, list[str]]:
    assert PILImage is not None
    with PILImage.open(io.BytesIO(data)) as im:
        w, h = im.size
        rgb = im.convert("RGB")
        rgb.thumbnail((96, 96))
        samples = list(rgb.getdata())
        return w, h, select_distinct_palette(samples, count=5)


def find_fallback_pil_python() -> str | None:
    candidates = [
        r"D:\ProgramData\Anaconda\python.exe",
        shutil.which("python3"),
        shutil.which("python"),
    ]
    for cand in candidates:
        if not cand or os.path.abspath(cand) == os.path.abspath(sys.executable):
            continue
        if Path(cand).exists():
            try:
                res = subprocess.run(
                    [cand, "-c", "import PIL"],
                    capture_output=True,
                    timeout=5,
                )
                if res.returncode == 0:
                    return cand
            except Exception:
                continue
    return None


def batch_extract_via_subprocess(
    pil_python: str,
    image_blobs: dict[str, bytes],
) -> dict[str, tuple[int, int, list[str]]]:
    """Decode JPEG/WebP/PNG dimensions & palettes via an available Pillow Python."""
    if not image_blobs:
        return {}
    tmp_dir = ROOT_DIR / "tmp_img_cache"
    tmp_dir.mkdir(exist_ok=True)
    paths_map: dict[str, str] = {}
    try:
        for fid, raw in image_blobs.items():
            ext = ".png"
            if raw[:2] == b"\xff\xd8":
                ext = ".jpg"
            elif raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
                ext = ".webp"
            p = tmp_dir / f"{re.sub(r'[^A-Za-z0-9_.-]', '_', fid)}{ext}"
            p.write_bytes(raw)
            paths_map[fid] = str(p)

        helper = """
import json, sys
from PIL import Image

def dist2(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2

def extract(path):
    with Image.open(path) as im:
        w, h = im.size
        rgb = im.convert("RGB")
        rgb.thumbnail((96, 96))
        buckets = {}
        for r, g, b in rgb.getdata():
            mx, mn = max(r, g, b), min(r, g, b)
            if mx > 242 and mn > 230: continue
            if mx < 28: continue
            if (mx - mn) < 18 and (mx > 190 or mn < 60): continue
            q = (r >> 4, g >> 4, b >> 4)
            buckets.setdefault(q, []).append((r, g, b))
        ranked = sorted(buckets.values(), key=len, reverse=True)
        chosen = []
        for pts in ranked:
            n = len(pts)
            avg = (sum(p[0] for p in pts)//n, sum(p[1] for p in pts)//n, sum(p[2] for p in pts)//n)
            if all(dist2(avg, c) > 2200 for c in chosen):
                chosen.append(avg)
                if len(chosen) >= 5: break
        if len(chosen) < 5:
            for pts in ranked:
                n = len(pts)
                avg = (sum(p[0] for p in pts)//n, sum(p[1] for p in pts)//n, sum(p[2] for p in pts)//n)
                if all(dist2(avg, c) > 650 for c in chosen):
                    chosen.append(avg)
                    if len(chosen) >= 5: break
        for d in [(43,92,143),(200,75,49),(46,139,87),(217,140,38),(114,78,152)]:
            if len(chosen) >= 5: break
            if all(dist2(d, c) > 900 for c in chosen): chosen.append(d)
        pal = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in chosen[:5]]
        return [w, h, pal]

mapping = json.loads(sys.stdin.read())
out = {}
for fid, path in mapping.items():
    try:
        out[fid] = extract(path)
    except Exception:
        pass
print(json.dumps(out))
"""
        proc = subprocess.run(
            [pil_python, "-X", "utf8", "-c", helper],
            input=json.dumps(paths_map),
            text=True,
            capture_output=True,
            timeout=90,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            parsed = json.loads(proc.stdout.strip())
            return {k: (int(v[0]), int(v[1]), list(v[2])) for k, v in parsed.items()}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return {}


def fetch_pmc_oai_xml(sess: requests.Session, pmcid: str, timeout: int = 6) -> str:
    num = pmcid.replace("PMC", "").strip()
    if not num.isdigit():
        return ""
    try:
        r = sess.get(
            "https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh/",
            params={
                "verb": "GetRecord",
                "identifier": f"oai:pubmedcentral.nih.gov:{num}",
                "metadataPrefix": "pmc",
            },
            timeout=timeout,
        )
        if r.status_code == 200 and "<fig" in r.text:
            return r.text
    except Exception:
        pass
    return ""


def parse_first_fig_from_jats(xml_text: str) -> tuple[str, str, bool]:
    """Extract first figure label, caption text, and whether it is a graphical abstract."""
    if not xml_text:
        return "Fig. 1", "", False
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return "Fig. 1", "", False

    figs = [el for el in root.iter() if el.tag.endswith("}fig") or el.tag == "fig"]
    for fig in figs:
        fig_id = (fig.get("id") or "").lower()
        fig_type = (fig.get("fig-type") or "").lower()
        is_ga = "undfig" in fig_id or "ga" in fig_id or "fx" in fig_id or "abstract" in fig_type
        label = ""
        caption_parts: list[str] = []
        for child in fig:
            tag = child.tag.split("}")[-1]
            if tag == "label":
                label = clean_text("".join(child.itertext()))
            elif tag == "caption":
                caption_parts.append(clean_text("".join(child.itertext())))
        caption = " ".join(p for p in caption_parts if p).strip()
        if is_ga or re.search(r"\b(fig\.?\s*1|figure\s*1|f1)\b", f"{label} {fig_id}", re.I):
            return (label or ("Graphical Abstract" if is_ga else "Fig. 1")), caption, is_ga
    if figs:
        fig = figs[0]
        label = ""
        cap = ""
        for child in fig:
            tag = child.tag.split("}")[-1]
            if tag == "label":
                label = clean_text("".join(child.itertext()))
            elif tag == "caption":
                cap = clean_text("".join(child.itertext()))
        return label or "Fig. 1", cap, False
    return "Fig. 1", "", False


def resolve_nature_figure(
    sess: requests.Session,
    doi: str,
    pmcid: str,
    fast_captions: bool = True,
) -> dict[str, Any] | None:
    m = NATURE_DOI_RE.match(doi)
    if not m:
        return None
    jcode, yy, artnum = m.group(1), m.group(2), int(m.group(3))
    full_year = 2000 + int(yy)
    doi_enc = quote(doi, safe="")
    thumb_url = f"https://media.springernature.com/lw685/springer-static/image/art%3A{doi_enc}/MediaObjects/{jcode}_{full_year}_{artnum}_Fig1_HTML.png"
    highres_url = f"https://media.springernature.com/full/springer-static/image/art%3A{doi_enc}/MediaObjects/{jcode}_{full_year}_{artnum}_Fig1_HTML.png"
    try:
        r = sess.get(thumb_url, timeout=6)
        if r.status_code != 200 or len(r.content) < 4000:
            return None
        img_bytes = r.content
    except Exception:
        return None

    label, caption, is_ga = "Fig. 1", "", False
    if not fast_captions and pmcid:
        xml_text = fetch_pmc_oai_xml(sess, pmcid, timeout=5)
        label, caption, is_ga = parse_first_fig_from_jats(xml_text)
    return {
        "image": thumb_url,
        "highres": highres_url,
        "figure_label": label or "Fig. 1",
        "caption": caption,
        "is_ga": is_ga,
        "img_bytes": img_bytes,
    }


def resolve_pmc_s3_figure(
    sess: requests.Session,
    pmcid: str,
    fast_captions: bool = True,
) -> dict[str, Any] | None:
    """Resolve OA figure and caption directly from AWS Open Data bucket pmc-oa-opendata."""
    if not pmcid:
        return None
    base_s3 = "https://pmc-oa-opendata.s3.amazonaws.com"
    try:
        r = sess.get(base_s3 + "/", params={"list-type": "2", "prefix": f"{pmcid}."}, timeout=7)
        if r.status_code != 200:
            return None
        keys = re.findall(r"<Key>([^<]+)</Key>", r.text)
    except Exception:
        return None

    img_keys = [
        k for k in keys
        if re.search(r"\.(?:webp|jpg|jpeg|png)$", k, re.I)
        and "supplement" not in k.lower()
    ]
    if not img_keys:
        return None

    chosen_key = ""
    label = "Fig. 1"
    caption = ""
    is_ga = False

    if not fast_captions:
        xml_keys = [k for k in keys if k.endswith(".xml")]
        xml_text = ""
        if xml_keys:
            try:
                rx = sess.get(f"{base_s3}/{quote(xml_keys[0], safe='/')}", timeout=7)
                if rx.status_code == 200 and "<fig" in rx.text:
                    xml_text = rx.text
            except Exception:
                pass
        if not xml_text:
            xml_text = fetch_pmc_oai_xml(sess, pmcid, timeout=5)

        if xml_text:
            try:
                root = ET.fromstring(xml_text)
                figs = [el for el in root.iter() if el.tag.endswith("}fig") or el.tag == "fig"]
                parsed_figs: list[tuple[bool, str, str, list[str]]] = []
                for fig in figs:
                    fig_id = (fig.get("id") or "").lower()
                    fig_type = (fig.get("fig-type") or "").lower()
                    f_is_ga = "undfig" in fig_id or "ga" in fig_id or "fx" in fig_id or "abstract" in fig_type
                    lbl = ""
                    cap_parts: list[str] = []
                    hrefs: list[str] = []
                    for child in fig.iter():
                        tag = child.tag.split("}")[-1]
                        if tag == "label" and not lbl:
                            lbl = clean_text("".join(child.itertext()))
                        elif tag == "caption":
                            cap_parts.append(clean_text("".join(child.itertext())))
                        elif tag == "graphic":
                            for k_attr, v_attr in child.attrib.items():
                                if k_attr.endswith("href") and v_attr:
                                    hrefs.append(v_attr.strip())
                    f_cap = " ".join(p for p in cap_parts if p).strip()
                    parsed_figs.append((f_is_ga, lbl, f_cap, hrefs))

                def score_fig(item: tuple[bool, str, str, list[str]]) -> int:
                    f_is_ga, lbl, _c, _h = item
                    if f_is_ga:
                        return 0
                    if re.search(r"\b(fig\.?\s*1|figure\s*1|f1)\b", lbl, re.I):
                        return 1
                    return 2

                for f_is_ga, lbl, f_cap, hrefs in sorted(parsed_figs, key=score_fig):
                    for h in hrefs:
                        h_stem = Path(h).stem.lower()
                        match = next(
                            (ik for ik in img_keys if Path(ik).name.lower() == h.lower() or Path(ik).stem.lower() == h_stem),
                            None,
                        )
                        if match:
                            chosen_key = match
                            label = lbl or ("Graphical Abstract" if f_is_ga else "Fig. 1")
                            caption = f_cap
                            is_ga = f_is_ga
                            break
                    if chosen_key:
                        break
            except Exception:
                pass

    if not chosen_key:
        def key_rank(k: str) -> tuple[int, str]:
            name = Path(k).name.lower()
            if re.search(r"(?:^|[-_])(fx1|ga1)(?:\.|[-_])", name):
                return (0, name)
            if re.search(r"(?:^|[-_])(f0*1|fig0*1|gr0*1)(?:\.|[-_])", name):
                return (1, name)
            return (2, name)

        chosen_key = sorted(img_keys, key=key_rank)[0]
        is_ga = bool(re.search(r"(?:^|[-_])(fx1|ga1)(?:\.|[-_])", chosen_key.lower()))
        if is_ga:
            label = "Graphical Abstract"

    img_url = f"{base_s3}/{quote(chosen_key, safe='/')}"
    try:
        ir = sess.get(img_url, timeout=8)
        if ir.status_code != 200 or len(ir.content) < 4000:
            return None
        return {
            "image": img_url,
            "highres": img_url,
            "figure_label": label or ("Graphical Abstract" if is_ga else "Fig. 1"),
            "caption": caption,
            "is_ga": is_ga,
            "img_bytes": ir.content,
        }
    except Exception:
        return None


def clean_pii(raw: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", raw or "")
    if cleaned.startswith("S") and len(cleaned) >= 16:
        return cleaned
    return ""


def prefetch_cell_piis(
    cell_items: list[tuple[str, str]],
    crossref_workers: int = 2,
) -> dict[str, str]:
    """Batch-fetch Elsevier PIIs via NCBI esummary.fcgi (PMID -> PII) with Crossref fallback."""
    pii_cache: dict[str, str] = {}
    if not cell_items:
        return pii_cache

    # 1) Primary fast path: NCBI E-Utilities esummary.fcgi batch POST (150 PMIDs/request)
    pmid_to_dois: dict[str, list[str]] = {}
    for doi, pmid in cell_items:
        d_norm = (doi or "").strip().lower()
        p_norm = (pmid or "").strip()
        if d_norm and p_norm.isdigit():
            pmid_to_dois.setdefault(p_norm, []).append(d_norm)

    pmids = sorted(pmid_to_dois.keys())
    if pmids:
        sess = make_session()
        for i in range(0, len(pmids), 150):
            chunk = pmids[i : i + 150]
            try:
                r = sess.post(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                    data={"db": "pubmed", "id": ",".join(chunk), "retmode": "json"},
                    timeout=15,
                )
                if r.status_code == 429:
                    time.sleep(1.5)
                    r = sess.post(
                        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                        data={"db": "pubmed", "id": ",".join(chunk), "retmode": "json"},
                        timeout=15,
                    )
                if r.status_code == 200:
                    result = r.json().get("result", {})
                    for pmid in chunk:
                        entry = result.get(pmid)
                        if not isinstance(entry, dict):
                            continue
                        for aid in entry.get("articleids") or []:
                            if aid.get("idtype") == "pii":
                                pii = clean_pii(aid.get("value", ""))
                                if pii:
                                    for d_norm in pmid_to_dois.get(pmid, []):
                                        pii_cache[d_norm] = pii
                                    break
            except Exception:
                pass
            if i + 150 < len(pmids):
                time.sleep(0.35)

    # 2) Secondary fallback: Crossref batch filter (25 DOIs/chunk, low concurrency)
    missing_dois = sorted(
        {
            (doi or "").strip().lower()
            for doi, _ in cell_items
            if doi and (doi or "").strip().lower() not in pii_cache
        }
    )
    if missing_dois:
        chunks = [missing_dois[i : i + 25] for i in range(0, len(missing_dois), 25)]

        def fetch_chunk(chunk: list[str]) -> list[tuple[str, str]]:
            sess = make_session()
            out: list[tuple[str, str]] = []
            try:
                r = sess.get(
                    "https://api.crossref.org/works",
                    params={
                        "filter": ",".join(f"doi:{d}" for d in chunk),
                        "rows": len(chunk),
                        "select": "DOI,alternative-id",
                    },
                    timeout=14,
                )
                if r.status_code == 200:
                    for item in r.json().get("message", {}).get("items", []):
                        d = (item.get("DOI") or "").strip().lower()
                        for alt in item.get("alternative-id") or []:
                            pii = clean_pii(alt)
                            if pii:
                                out.append((d, pii))
                                break
            except Exception:
                pass
            return out

        with ThreadPoolExecutor(max_workers=crossref_workers) as pool:
            for pairs in pool.map(fetch_chunk, chunks):
                for d, pii in pairs:
                    pii_cache[d] = pii

    return pii_cache


def resolve_cell_figure(
    sess: requests.Session,
    doi: str,
    pmcid: str,
    pmid: str,
    prefer_ga: bool = False,
    pii_cache: dict[str, str] | None = None,
    fast_captions: bool = True,
) -> dict[str, Any] | None:
    pii = (pii_cache or {}).get(doi.lower(), "")
    xml_text = ""

    if not pii and not fast_captions and doi:
        try:
            r = sess.get(f"https://api.crossref.org/works/{quote(doi, safe='')}", timeout=5)
            if r.status_code == 200:
                alts = r.json().get("message", {}).get("alternative-id") or []
                for alt in alts:
                    clean_alt = re.sub(r"[^A-Za-z0-9]", "", alt)
                    if clean_alt.startswith("S") and len(clean_alt) >= 16:
                        pii = clean_alt
                        break
        except Exception:
            pass

    if not pii and pmid and not fast_captions:
        try:
            r = sess.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                params={"db": "pubmed", "id": pmid, "retmode": "json"},
                timeout=5,
            )
            aids = r.json().get("result", {}).get(pmid, {}).get("articleids", [])
            raw_pii = next((x["value"] for x in aids if x.get("idtype") == "pii"), "")
            if raw_pii.startswith("S"):
                pii = re.sub(r"[^A-Za-z0-9]", "", raw_pii)
        except Exception:
            pass

    if not pii and pmcid and not fast_captions:
        xml_text = fetch_pmc_oai_xml(sess, pmcid, timeout=5)
        if xml_text:
            m = re.search(r'<article-id pub-id-type="pii">([^<]+)</article-id>', xml_text)
            if m:
                pii = re.sub(r"[^A-Za-z0-9]", "", m.group(1))

    if pii:
        order = [("fx1", True, "Graphical Abstract"), ("gr1", False, "Fig. 1")] if prefer_ga else [("gr1", False, "Fig. 1"), ("fx1", True, "Graphical Abstract")]
        for code, code_is_ga, fallback_lbl in order:
            thumb = f"https://ars.els-cdn.com/content/image/1-s2.0-{pii}-{code}.jpg"
            lrg = f"https://ars.els-cdn.com/content/image/1-s2.0-{pii}-{code}_lrg.jpg"
            try:
                rt = sess.get(thumb, timeout=6)
                if rt.status_code == 200 and len(rt.content) > 4000:
                    label, caption = (fallback_lbl if code_is_ga else "Fig. 1"), ""
                    if not fast_captions and pmcid:
                        if not xml_text:
                            xml_text = fetch_pmc_oai_xml(sess, pmcid, timeout=5)
                        j_lbl, caption, _ = parse_first_fig_from_jats(xml_text)
                        if not code_is_ga and j_lbl:
                            label = j_lbl
                    return {
                        "image": thumb,
                        "highres": lrg,
                        "figure_label": label,
                        "caption": caption,
                        "is_ga": code_is_ga,
                        "img_bytes": rt.content,
                    }
            except Exception:
                continue

    if pmcid:
        return resolve_pmc_s3_figure(sess, pmcid, fast_captions=fast_captions)
    return None


def discover_openalex_paginated(
    sess: requests.Session,
    issns: list[str],
    year: int,
    target_count: int = 200,
    oa_filter: str = "open_access.is_oa:true",
    require_pmcid: bool = False,
) -> list[dict[str, Any]]:
    issn_filter = "|".join(issns)
    flt = f"primary_location.source.issn:{issn_filter},{oa_filter},publication_year:{year}"
    if require_pmcid:
        flt += ",has_pmcid:true"
    sort_by = "cited_by_count:desc" if year < 2026 else "publication_date:desc"
    collected: list[dict[str, Any]] = []
    page = 1
    while len(collected) < target_count:
        per_page = min(200, max(25, target_count - len(collected)))
        params = {
            "filter": flt,
            "sort": sort_by,
            "per-page": per_page,
            "page": page,
            "select": (
                "id,doi,ids,title,publication_year,publication_date,cited_by_count,"
                "open_access,best_oa_location,primary_location,primary_topic,authorships,abstract_inverted_index"
            ),
        }
        try:
            r = sess.get("https://api.openalex.org/works", params=params, timeout=20)
            if r.status_code != 200:
                print(f"  OpenAlex status={r.status_code} year={year} page={page}: {r.text[:140]}")
                break
            batch = r.json().get("results", [])
            if not batch:
                break
            collected.extend(batch)
            if len(batch) < per_page:
                break
            page += 1
        except Exception as e:
            print(f"  OpenAlex err year={year} page={page}: {e}")
            break
    return collected[:target_count]


def match_journal_from_work(
    work: dict[str, Any],
    issn_map: dict[str, dict[str, Any]],
    title_map: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    src = (work.get("primary_location") or {}).get("source") or {}
    for issn in (src.get("issn") or []):
        if issn in issn_map:
            return issn_map[issn]
    if src.get("issn_l") in issn_map:
        return issn_map[src["issn_l"]]
    disp = (src.get("display_name") or "").strip().lower()
    if disp in title_map:
        return title_map[disp]
    return None


def resolve_candidate(
    candidate: tuple[dict[str, Any], dict[str, Any], int],
    idx: int,
    pii_cache: dict[str, str] | None = None,
    fast_captions: bool = True,
) -> tuple[dict[str, Any], bytes] | None:
    journal, work, year = candidate
    sess = make_session()
    doi_url = work.get("doi") or ""
    doi = doi_url.replace("https://doi.org/", "").strip()
    ids = work.get("ids") or {}
    pmcid_raw = (ids.get("pmcid") or "").rstrip("/").split("/")[-1]
    pmcid = f"PMC{pmcid_raw}" if pmcid_raw and not pmcid_raw.startswith("PMC") else pmcid_raw
    pmid_raw = (ids.get("pmid") or "").rstrip("/").split("/")[-1]
    if not doi:
        return None

    title = clean_text(work.get("title") or "")
    if not title or len(title) < 8:
        return None

    family = journal["family"]
    resolved: dict[str, Any] | None = None

    if family == "nature":
        resolved = resolve_nature_figure(sess, doi, pmcid, fast_captions=fast_captions)
        if not resolved and pmcid:
            resolved = resolve_pmc_s3_figure(sess, pmcid, fast_captions=fast_captions)
    elif family == "cell":
        resolved = resolve_cell_figure(
            sess,
            doi,
            pmcid,
            pmid_raw,
            prefer_ga=(idx % 2 == 0),
            pii_cache=pii_cache,
            fast_captions=fast_captions,
        )
    else:
        if pmcid:
            resolved = resolve_pmc_s3_figure(sess, pmcid, fast_captions=fast_captions)

    if not resolved:
        return None

    abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
    caption = resolved["caption"] or abstract[:480]
    discipline = classify_discipline(journal, work, abstract, caption)
    pattern = classify_pattern(resolved["figure_label"], caption, title, resolved["is_ga"])

    authors = [
        (a.get("author") or {}).get("display_name", "")
        for a in (work.get("authorships") or [])[:8]
        if (a.get("author") or {}).get("display_name")
    ]
    best_loc = work.get("best_oa_location") or {}
    oa_info = work.get("open_access") or {}
    lic = (best_loc.get("license") or oa_info.get("oa_status") or "open-access").upper()
    if lic == "CC-BY":
        lic = "CC BY 4.0"

    id_suffix = pmcid.lower() if pmcid else re.sub(r"[^a-z0-9]+", "-", doi.lower()).strip("-")
    fig_id = f"{journal['slug']}-{year}-{id_suffix}"

    w_px, h_px, pal = 0, 0, []
    raw_bytes = resolved["img_bytes"]
    if PILImage is not None:
        try:
            w_px, h_px, pal = extract_with_pil(raw_bytes)
            raw_bytes = b""
        except Exception:
            pass

    record = {
        "id": fig_id,
        "title": title,
        "authors": authors,
        "journal": journal["title"],
        "journal_short": journal["short"],
        "journal_slug": journal["slug"],
        "family": family,
        "tier": journal["tier"],
        "year": int(work.get("publication_year") or year),
        "pub_date": work.get("publication_date") or f"{year}-01-01",
        "discipline": discipline,
        "pattern": pattern,
        "figure_label": resolved["figure_label"],
        "caption": caption[:900],
        "doi": doi,
        "pmcid": pmcid,
        "license": lic,
        "oa_status": oa_info.get("oa_status") or "oa",
        "citations": int(work.get("cited_by_count") or 0),
        "image": resolved["image"],
        "highres": resolved["highres"],
        "paper": f"https://doi.org/{doi}",
        "pmc_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/" if pmcid else "",
        "palette": pal,
        "w": w_px,
        "h": h_px,
    }
    return record, raw_bytes


def hydrate_dimensions_and_palettes(
    items: list[tuple[dict[str, Any], bytes]],
) -> list[dict[str, Any]]:
    need_subprocess: dict[str, bytes] = {}
    records: list[dict[str, Any]] = []

    for rec, img_bytes in items:
        fid = rec["id"]
        if rec.get("w", 0) > 0 and rec.get("h", 0) > 0 and len(rec.get("palette", [])) >= 5:
            records.append(rec)
            continue
        if PILImage is not None and img_bytes:
            try:
                w, h, pal = extract_with_pil(img_bytes)
                rec["w"], rec["h"], rec["palette"] = w, h, pal
                records.append(rec)
                continue
            except Exception:
                pass

        # Pure-Python path
        if img_bytes:
            w, h, samples = extract_png_samples_pure(img_bytes)
            if w > 0 and h > 0 and samples:
                rec["w"], rec["h"], rec["palette"] = w, h, select_distinct_palette(samples, 5)
            else:
                pw, ph = get_image_dimensions_pure(img_bytes)
                rec["w"], rec["h"] = pw, ph
                need_subprocess[fid] = img_bytes
        records.append(rec)

    if need_subprocess:
        pil_py = find_fallback_pil_python()
        if pil_py:
            decoded = batch_extract_via_subprocess(pil_py, need_subprocess)
            for rec in records:
                if rec["id"] in decoded:
                    w, h, pal = decoded[rec["id"]]
                    rec["w"], rec["h"], rec["palette"] = w, h, pal

    # Final fallback guard so every entry has valid dimensions and 5 colors
    final: list[dict[str, Any]] = []
    for rec in records:
        if rec["w"] <= 0 or rec["h"] <= 0:
            rec["w"], rec["h"] = 1200, 800
        if len(rec["palette"]) < 5:
            rec["palette"] = select_distinct_palette([], 5)
        final.append(rec)
    return final


def build_gallery_meta(journals_cfg: dict[str, Any], figures: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(figures),
        "years": sorted({f["year"] for f in figures}, reverse=True),
        "families": journals_cfg["families"],
        "tiers": journals_cfg["tiers"],
        "disciplines": journals_cfg["disciplines"],
        "patterns": journals_cfg["patterns"],
    }


def interleave_tier_candidates(
    items: list[tuple[dict[str, Any], dict[str, Any], int]],
) -> list[tuple[dict[str, Any], dict[str, Any], int]]:
    """Order within a (family, tier) bucket by round-robin across journals, newest & most cited first."""
    by_journal: dict[str, list[tuple[dict[str, Any], dict[str, Any], int]]] = {}
    for c in items:
        by_journal.setdefault(c[0]["slug"], []).append(c)
    for slug in by_journal:
        by_journal[slug].sort(key=lambda c: (-int(c[2]), -int(c[1].get("cited_by_count") or 0)))

    slugs = sorted(by_journal.keys(), key=lambda s: len(by_journal[s]), reverse=True)
    ordered: list[tuple[dict[str, Any], dict[str, Any], int]] = []
    idx = 0
    while True:
        added = False
        for s in slugs:
            lst = by_journal[s]
            if idx < len(lst):
                ordered.append(lst[idx])
                added = True
        if not added:
            break
        idx += 1
    return ordered


def write_outputs(journals_cfg: dict[str, Any], figures: list[dict[str, Any]]) -> None:
    tier_rank = {"flagship": 0, "subjournal": 1, "oa-series": 2}
    figures.sort(
        key=lambda f: (
            tier_rank.get(f["tier"], 9),
            -int(f["year"]),
            f.get("family", ""),
            f.get("journal_slug", ""),
            f.get("id", ""),
        )
    )

    meta = build_gallery_meta(journals_cfg, figures)
    FIGURES_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURES_JSON_PATH.write_text(
        json.dumps({"meta": meta, "figures": figures}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_JS_PATH.write_text(
        f"window.GALLERY_META = {json.dumps(meta, ensure_ascii=False)};\n"
        f"window.FIGURES = {json.dumps(figures, ensure_ascii=False)};\n",
        encoding="utf-8",
    )


def main() -> int:
    cur_yr = datetime.now(timezone.utc).year
    parser = argparse.ArgumentParser(description="Crawl Open Access NCS recent-3-year main figures")
    parser.add_argument("--years", nargs="+", type=int, default=[cur_yr, cur_yr - 1, cur_yr - 2])
    parser.add_argument("--families", nargs="+", default=["nature", "science", "cell"])
    parser.add_argument("--merge", action="store_true", help="Merge newly crawled figures with existing data/figures.json")
    parser.add_argument("--target-total", type=int, default=3100, help="Target total figures when stopping early (0 = unlimited)")
    parser.add_argument("--flagship-per-year", type=int, default=0, help="Override flagship quota per journal/year")
    parser.add_argument("--subjournal-per-year", type=int, default=0, help="Override subjournal quota per batch/year")
    parser.add_argument("--oa-series-per-year", type=int, default=0, help="Override oa-series quota per batch/year")
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--full-captions", action="store_true", help="Fetch JATS XML captions per article (slower)")
    args = parser.parse_args()

    fast_captions = not args.full_captions
    journals_cfg = json.loads(JOURNALS_PATH.read_text(encoding="utf-8"))
    target_families = set(args.families)
    journals: list[dict[str, Any]] = [j for j in journals_cfg["journals"] if j["family"] in target_families]

    issn_map: dict[str, dict[str, Any]] = {}
    title_map: dict[str, dict[str, Any]] = {}
    for j in journals:
        for issn in j["issn"]:
            issn_map[issn] = j
        title_map[j["title"].lower()] = j
        for et in j.get("epmc_titles", []):
            title_map[et.lower()] = j

    existing_by_doi: dict[str, dict[str, Any]] = {}
    if args.merge and FIGURES_JSON_PATH.exists():
        try:
            existing = json.loads(FIGURES_JSON_PATH.read_text(encoding="utf-8")).get("figures", [])
            for f in existing:
                if f.get("doi"):
                    existing_by_doi[f["doi"].strip().lower()] = f
            print(f"Loaded {len(existing_by_doi)} existing figures for merge (skipping already crawled DOIs).", flush=True)
        except Exception as e:
            print(f"Warning: could not load existing figures ({e}).", flush=True)

    # Build priority-ordered OpenAlex discovery batches:
    # 1) Flagships (Nature, Cell, Science) -> 2) Major Sub-journals -> 3) Broad/Minor OA Sub-journals
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for j in journals:
        if j["tier"] == "flagship":
            gkey = (j["tier"], j["family"], j["slug"])
        elif j["tier"] == "subjournal":
            if j["family"] == "science":
                gkey = (j["tier"], j["family"], j["slug"])
            else:
                gkey = (j["tier"], j["family"], j["default_discipline"])
        else:
            gkey = (j["tier"], j["family"], j["slug"] if j["family"] != "cell" else "cell-oa")
        grouped.setdefault(gkey, []).append(j)

    tier_order = {"flagship": 0, "subjournal": 1, "oa-series": 2}
    ordered_groups = sorted(grouped.items(), key=lambda kv: (tier_order.get(kv[0][0], 9), kv[0][1], kv[0][2]))

    batches: list[tuple[list[dict[str, Any]], int, str, bool]] = []
    for (tier, fam, slug_or_disc), jlist in ordered_groups:
        chunk_step = 4 if fam == "cell" else 8
        for i in range(0, len(jlist), chunk_step):
            chunk = jlist[i : i + chunk_step]
            if tier == "flagship":
                default_q = 400 if fam == "nature" else (350 if fam == "cell" else 300)
                quota = args.flagship_per_year or default_q
            elif tier == "subjournal":
                default_q = 240 if fam == "cell" else 200
                quota = args.subjournal_per_year or default_q
            else:
                default_q = 260 if fam == "science" else (140 if fam == "cell" else 150)
                quota = args.oa_series_per_year or default_q

            oa_filter = "open_access.oa_status:gold|hybrid|diamond" if fam == "nature" else "open_access.is_oa:true"
            require_pmcid = fam == "science"
            batches.append((chunk, quota, oa_filter, require_pmcid))

    sess = make_session()
    candidates: list[tuple[dict[str, Any], dict[str, Any], int]] = []
    seen_dois: set[str] = set(existing_by_doi.keys())

    print(f"Discovering Open Access NCS papers ({len(batches)} groups x {len(args.years)} years)...", flush=True)
    for jlist, quota, oa_filter, require_pmcid in batches:
        issns: list[str] = []
        for j in jlist:
            issns.extend(j["issn"])
        for yr in args.years:
            works = discover_openalex_paginated(
                sess,
                issns,
                yr,
                target_count=quota,
                oa_filter=oa_filter,
                require_pmcid=require_pmcid,
            )
            for w in works:
                doi = (w.get("doi") or "").replace("https://doi.org/", "").strip().lower()
                if not doi or doi in seen_dois:
                    continue
                matched_j = match_journal_from_work(w, issn_map, title_map) or jlist[0]
                seen_dois.add(doi)
                candidates.append((matched_j, w, yr))

    # Order candidates strictly Flagship -> Major Sub-journals -> Minor OA within each family,
    # round-robin interleaved across journals inside each tier
    by_family: dict[str, list[tuple[dict[str, Any], dict[str, Any], int]]] = {}
    for c in candidates:
        fam = c[0]["family"]
        by_family.setdefault(fam, []).append(c)

    ordered_by_family: dict[str, list[tuple[dict[str, Any], dict[str, Any], int]]] = {}
    for fam, fam_cands in by_family.items():
        fam_ordered: list[tuple[dict[str, Any], dict[str, Any], int]] = []
        for tier_name in ("flagship", "subjournal", "oa-series"):
            tier_cands = [c for c in fam_cands if c[0]["tier"] == tier_name]
            if tier_cands:
                fam_ordered.extend(interleave_tier_candidates(tier_cands))
        ordered_by_family[fam] = fam_ordered

    ordered_candidates = [c for fam in ordered_by_family for c in ordered_by_family[fam]]
    print(f"Discovered {len(ordered_candidates)} new candidate OA works (Flagships first).", flush=True)

    # Pre-fetch Elsevier PIIs via NCBI esummary.fcgi (PMID -> PII) with Crossref fallback
    cell_items: list[tuple[str, str]] = [
        (
            (w.get("doi") or "").replace("https://doi.org/", "").strip(),
            ((w.get("ids") or {}).get("pmid") or "").rstrip("/").split("/")[-1],
        )
        for j, w, _yr in ordered_candidates
        if j["family"] == "cell"
    ]
    pii_cache: dict[str, str] = {}
    if cell_items:
        t_pii = time.time()
        pii_cache = prefetch_cell_piis(cell_items, crossref_workers=2)
        print(f"Pre-fetched {len(pii_cache)}/{len(cell_items)} Cell Press PIIs in {time.time() - t_pii:.1f}s.", flush=True)

    t0 = time.time()
    resolved_items: list[tuple[dict[str, Any], bytes]] = []
    needed = max(0, args.target_total - len(existing_by_doi)) if args.target_total > 0 else len(ordered_candidates)

    # Resolve each requested family cleanly (preserving Flagship > Major Sub-journal > Minor OA within each family)
    active_fams = [f for f in args.families if ordered_by_family.get(f)]
    fam_count = max(1, len(active_fams))
    chunk_size = 240
    checked_total = 0

    for fam_idx, fam in enumerate(active_fams):
        remaining_needed = max(0, needed - len(resolved_items))
        if remaining_needed == 0:
            break
        remaining_fams = fam_count - fam_idx
        fam_quota = remaining_needed // remaining_fams if remaining_fams > 1 else remaining_needed
        fam_target_resolved = len(resolved_items) + fam_quota
        fam_cands = ordered_by_family[fam]
        print(f"Resolving family '{fam}' ({len(fam_cands)} candidates, quota {fam_quota})...", flush=True)

        for start in range(0, len(fam_cands), chunk_size):
            if len(resolved_items) >= fam_target_resolved:
                break
            batch = fam_cands[start : start + chunk_size]
            with ThreadPoolExecutor(max_workers=args.workers) as pool:
                futs = [
                    pool.submit(resolve_candidate, cand, start + i, pii_cache, fast_captions)
                    for i, cand in enumerate(batch)
                ]
                for fut in as_completed(futs):
                    checked_total += 1
                    try:
                        res = fut.result()
                        if res is not None:
                            resolved_items.append(res)
                    except Exception:
                        pass
            print(
                f"  [{fam}] Progress: {checked_total}/{len(ordered_candidates)} checked, {len(resolved_items)} new resolved "
                f"(total ~{len(existing_by_doi) + len(resolved_items)}) [{time.time() - t0:.1f}s]",
                flush=True,
            )
            if len(resolved_items) >= 400 and (len(resolved_items) % 400 < chunk_size):
                ckpt_figs = hydrate_dimensions_and_palettes(resolved_items)
                merged_map = dict(existing_by_doi)
                for f in ckpt_figs:
                    merged_map[f["doi"].strip().lower()] = f
                write_outputs(journals_cfg, list(merged_map.values()))

    print(f"Resolved {len(resolved_items)} new valid main figures in {time.time() - t0:.1f}s. Finalizing palettes...", flush=True)
    new_figures = hydrate_dimensions_and_palettes(resolved_items)

    merged_by_doi = dict(existing_by_doi)
    for f in new_figures:
        merged_by_doi[f["doi"].strip().lower()] = f
    all_figures = list(merged_by_doi.values())

    write_outputs(journals_cfg, all_figures)
    print(f"Saved {len(all_figures)} total figures to {FIGURES_JSON_PATH} and {FIGURES_JS_PATH}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
