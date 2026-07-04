from __future__ import annotations

import csv
import html
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CACHE_DIR = os.path.join(ROOT, "work", "oxford_cache")
REPORT_PATH = os.path.join(ROOT, "work", "oxford_verification_report.csv")


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


combined = load_module("verify_combined", os.path.join(ROOT, "work", "generate_flashcards_combined.py"))
word_roots = load_module("verify_word_roots", os.path.join(ROOT, "work", "word_roots.py"))


def strip_tags(value: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def fetch_url(url: str) -> tuple[int | None, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            text = response.read().decode("utf-8", errors="ignore")
            return response.status, text
    except urllib.error.HTTPError as exc:
        return exc.code, ""
    except Exception:
        return None, ""


def fetch_oxford(word: str) -> tuple[int | None, str]:
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", word.lower())
    path = os.path.join(CACHE_DIR, f"{safe}.html")
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return 200, f.read()

    quoted = urllib.parse.quote(word.lower())
    urls = [
        f"https://www.oxfordlearnersdictionaries.com/us/definition/english/{quoted}?q={quoted}",
        f"https://www.oxfordlearnersdictionaries.com/us/definition/american_english/{quoted}?q={quoted}",
    ]
    last_status: int | None = None
    for url in urls:
        status, text = fetch_url(url)
        last_status = status
        if status == 200 and "Word not found in the dictionary" not in text:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            time.sleep(0.15)
            return status, text
    return last_status, ""


def parse_oxford(text: str) -> dict[str, str]:
    pos = ""
    defs: list[str] = []
    examples: list[str] = []
    synonyms: list[str] = []
    origin = ""

    entry_match = re.search(r'<div id="entryContent".*?(?:<div id="ring-links-box"|<div class="responsive_row")', text, flags=re.I | re.S)
    entry = entry_match.group(0) if entry_match else text

    pos_match = re.search(r'<span class="pos"[^>]*>(.*?)</span>', entry, flags=re.I | re.S)
    if pos_match:
        pos = strip_tags(pos_match.group(1)).lower()

    defs = [strip_tags(m) for m in re.findall(r'<span class="def"[^>]*>(.*?)</span>', entry, flags=re.I | re.S)]
    examples = [strip_tags(m) for m in re.findall(r'<span class="x"[^>]*>(.*?)</span>', entry, flags=re.I | re.S)]
    synonyms = [strip_tags(m) for m in re.findall(r'<span class="xh">(.*?)</span>', entry, flags=re.I | re.S)]

    origin_match = re.search(r'<span class="box_title">Word Origin</span><span class="body">(.*?)(?:</span></span></span>|</span></span></li>|</div></ol>)', entry, flags=re.I | re.S)
    if origin_match:
        origin = strip_tags(origin_match.group(1))

    return {
        "oxford_pos": pos,
        "oxford_defs": " | ".join(defs[:3]),
        "oxford_example": examples[0] if examples else "",
        "oxford_synonyms": ", ".join(dict.fromkeys(synonyms[:6])),
        "oxford_origin": origin,
    }


def main() -> None:
    cards = combined.build_cards()
    roots = word_roots.load_roots()
    unique = []
    seen = set()
    for card in cards:
        word = card.entry.word
        if word.lower() not in seen:
            seen.add(word.lower())
            unique.append(card.entry)

    rows = []
    for i, entry in enumerate(unique, start=1):
        status, text = fetch_oxford(entry.word)
        parsed = parse_oxford(text) if text else {"oxford_pos": "", "oxford_defs": "", "oxford_example": "", "oxford_synonyms": "", "oxford_origin": ""}
        root = roots.get(entry.word.lower(), "")
        pos_match = parsed["oxford_pos"] == entry.pos.lower() if parsed["oxford_pos"] else ""
        rows.append({
            "word": entry.word,
            "status": status,
            "current_pos": entry.pos,
            "oxford_pos": parsed["oxford_pos"],
            "pos_match": pos_match,
            "current_definition": entry.definition,
            "oxford_definitions": parsed["oxford_defs"],
            "current_synonyms": entry.synonyms,
            "oxford_synonyms": parsed["oxford_synonyms"],
            "current_root": root,
            "oxford_origin": parsed["oxford_origin"],
        })
        if i % 25 == 0:
            print(f"Checked {i}/{len(unique)}")

    with open(REPORT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Checked {len(rows)} unique words")
    print(f"Fetched OK: {sum(1 for r in rows if r['status'] == 200)}")
    print(f"POS mismatches: {sum(1 for r in rows if r['pos_match'] is False)}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
