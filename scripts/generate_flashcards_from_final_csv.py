from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARTIFACTS_DIR = os.path.join(ROOT, "artifacts")
SITE_DATA_DIR = os.path.join(ROOT, "data")

COMPLETE_CSV = os.path.join(ARTIFACTS_DIR, "vocabulary_flashcards_complete_deduped_source.csv")
COMPLETE_PDF = os.path.join(ARTIFACTS_DIR, "vocabulary_flashcards_complete_deduped.pdf")
SITE_JSON = os.path.join(SITE_DATA_DIR, "cards.json")
SITE_JS = os.path.join(SITE_DATA_DIR, "cards.js")

PAGE_W, PAGE_H = A4
COLS = 2
ROWS = 5
CARD_W = PAGE_W / COLS
CARD_H = PAGE_H / ROWS
CARDS_PER_SHEET = COLS * ROWS
FRONT_GRID_LEFT = 0
GRID_TOP = PAGE_H
FRONT_GRID_RIGHT = FRONT_GRID_LEFT + COLS * CARD_W
GRID_BOTTOM = GRID_TOP - ROWS * CARD_H
BACK_GRID_LEFT = PAGE_W - FRONT_GRID_RIGHT

POS_FULL = {
    "adj": "adjective",
    "adjective": "adjective",
    "n": "noun",
    "noun": "noun",
    "v": "verb",
    "verb": "verb",
    "adv": "adverb",
    "adverb": "adverb",
}

POS_ABBREV = {
    "adjective": "adj",
    "noun": "n",
    "verb": "v",
    "adverb": "adv",
}


@dataclass(frozen=True)
class Entry:
    card_number: str
    word: str
    part_of_speech: str
    definition: str
    sample_sentence: str
    synonyms_top_3: str
    antonyms_top_3: str
    root: str


def normalize_pos(value: str) -> str:
    return POS_FULL.get(value.strip().lower(), value.strip().lower())


def normalize_row(row: dict[str, str]) -> Entry:
    return Entry(
        card_number=row.get("card_number", ""),
        word=row["word"].strip(),
        part_of_speech=normalize_pos(row["part_of_speech"]),
        definition=row["definition"].strip(),
        sample_sentence=row["sample_sentence"].strip(),
        synonyms_top_3=row["synonyms_top_3"].strip(),
        antonyms_top_3=row["antonyms_top_3"].strip(),
        root=row["root"].strip(),
    )


def read_entries(path: str) -> list[Entry]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [normalize_row(row) for row in csv.DictReader(f)]


def dedupe_entries(entries: list[Entry]) -> tuple[list[Entry], int]:
    by_word: dict[str, Entry] = {}
    order: list[str] = []
    duplicate_count = 0

    for entry in entries:
        key = entry.word.lower()
        if key not in by_word:
            order.append(key)
        else:
            duplicate_count += 1
        by_word[key] = entry

    merged = []
    for index, key in enumerate(order, start=1):
        entry = by_word[key]
        merged.append(Entry(str(index), entry.word, entry.part_of_speech, entry.definition, entry.sample_sentence, entry.synonyms_top_3, entry.antonyms_top_3, entry.root))
    return merged, duplicate_count


def fit_font_size(text: str, font: str, max_size: float, min_size: float, width: float) -> float:
    size = max_size
    while size > min_size and stringWidth(text, font, size) > width:
        size -= 0.5
    return size


def wrap_text(text: str, font: str, size: float, width: float) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if stringWidth(candidate, font, size) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def limited_lines(text: str, font: str, size: float, width: float, max_lines: int) -> list[str]:
    lines = wrap_text(text, font, size, width)
    if len(lines) <= max_lines:
        return lines
    clipped = lines[:max_lines]
    last = clipped[-1]
    while last and stringWidth(f"{last}...", font, size) > width:
        last = last[:-1].rstrip()
    clipped[-1] = f"{last}..." if last else "..."
    return clipped


def grid_left(side: str) -> float:
    return BACK_GRID_LEFT if side == "back" else FRONT_GRID_LEFT


def draw_cut_guides(c: canvas.Canvas, side: str = "front") -> None:
    c.saveState()
    c.setStrokeColor(colors.HexColor("#606B78"))
    c.setLineWidth(0.75)
    left = grid_left(side)
    right = left + COLS * CARD_W
    bottom = GRID_BOTTOM
    top = GRID_TOP

    for col in range(COLS + 1):
        x = left + col * CARD_W
        c.line(x, bottom, x, top)
    for row in range(ROWS + 1):
        y = GRID_BOTTOM + row * CARD_H
        c.line(left, y, right, y)
    c.setLineWidth(1.05)
    c.rect(left, bottom, right - left, top - bottom, stroke=1, fill=0)
    c.restoreState()


def card_origin(row: int, col: int, side: str = "front") -> tuple[float, float]:
    x = grid_left(side) + col * CARD_W
    y = GRID_TOP - (row + 1) * CARD_H
    return x, y


def draw_front(c: canvas.Canvas, entry: Entry, row: int, col: int) -> None:
    x, y = card_origin(row, col)
    c.saveState()
    c.setFillColor(colors.HexColor("#111418"))
    font = "Helvetica-Bold"
    font_size = fit_font_size(entry.word, font, 39, 19, CARD_W - 18)
    c.setFont(font, font_size)
    c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 - font_size * 0.35, entry.word)
    c.restoreState()


def draw_ruled_field(c: canvas.Canvas, label: str, text: str, x: float, y: float, width: float, row_h: float, max_lines: int, body_size: float = 8.0) -> float:
    label_w = 50
    text_x = x + label_w
    text_w = width - label_w
    line_y = y - row_h + 5.5

    c.setStrokeColor(colors.HexColor("#8E98A6"))
    c.setLineWidth(0.45)
    c.line(x, line_y, x + width, line_y)

    c.setFillColor(colors.HexColor("#5B5F66"))
    c.setFont("Helvetica-Bold", 7.6)
    c.drawString(x, y - 10, label)

    c.setFillColor(colors.HexColor("#15171A"))
    c.setFont("Helvetica", body_size)
    text_y = y - 10
    for line in limited_lines(text, "Helvetica", body_size, text_w, max_lines):
        c.drawString(text_x, text_y, line)
        text_y -= body_size + 2.1
    return y - row_h


def draw_back(c: canvas.Canvas, entry: Entry, row: int, col: int) -> None:
    x, y = card_origin(row, col, "back")
    pad = 10
    inner_x = x + pad
    inner_y = y + CARD_H - pad
    inner_w = CARD_W - pad * 2

    pos = POS_ABBREV.get(entry.part_of_speech, entry.part_of_speech)
    definition = f"({pos}) {entry.definition}"
    c.setFillColor(colors.HexColor("#111418"))
    c.setFont("Helvetica-Bold", 9.7)
    line_y = inner_y - 14
    for line in limited_lines(definition, "Helvetica-Bold", 9.7, inner_w, 3):
        c.drawCentredString(inner_x + inner_w / 2, line_y, line)
        line_y -= 10.8

    c.setStrokeColor(colors.HexColor("#9099A6"))
    c.setLineWidth(0.45)
    c.line(inner_x, line_y + 4, inner_x + inner_w, line_y + 4)

    body_y = line_y - 6
    body_y = draw_ruled_field(c, "Synonym", entry.synonyms_top_3, inner_x, body_y, inner_w, 20, 2, 8.0)
    body_y = draw_ruled_field(c, "Antonym", entry.antonyms_top_3, inner_x, body_y, inner_w, 20, 2, 8.0)
    body_y = draw_ruled_field(c, "Sentence", entry.sample_sentence, inner_x, body_y, inner_w, 36, 3, 7.8)
    draw_ruled_field(c, "Root", entry.root, inner_x, body_y, inner_w, 28, 2, 7.8)


def write_csv(entries: list[Entry]) -> None:
    with open(COMPLETE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "card_number",
            "word",
            "part_of_speech",
            "definition",
            "sample_sentence",
            "synonyms_top_3",
            "antonyms_top_3",
            "root",
        ])
        for entry in entries:
            writer.writerow([
                entry.card_number,
                entry.word,
                entry.part_of_speech,
                entry.definition,
                entry.sample_sentence,
                entry.synonyms_top_3,
                entry.antonyms_top_3,
                entry.root,
            ])


def write_site_data(entries: list[Entry]) -> None:
    cards = [
        {
            "card_number": entry.card_number,
            "word": entry.word,
            "part_of_speech": entry.part_of_speech,
            "definition": entry.definition,
            "sample_sentence": entry.sample_sentence,
            "synonyms_top_3": entry.synonyms_top_3,
            "antonyms_top_3": entry.antonyms_top_3,
            "root": entry.root,
        }
        for entry in entries
    ]
    with open(SITE_JSON, "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)
        f.write("\n")
    with open(SITE_JS, "w", encoding="utf-8") as f:
        f.write("window.STEPHANIE_SAT_CARDS = ")
        json.dump(cards, f, indent=2, ensure_ascii=False)
        f.write(";\n")


def write_pdf(entries: list[Entry]) -> None:
    c = canvas.Canvas(COMPLETE_PDF, pagesize=A4)

    for sheet_start in range(0, len(entries), CARDS_PER_SHEET):
        batch = entries[sheet_start : sheet_start + CARDS_PER_SHEET]

        draw_cut_guides(c)
        for i, entry in enumerate(batch):
            row = i // COLS
            col = i % COLS
            draw_front(c, entry, row, col)
        c.showPage()

        draw_cut_guides(c, "back")
        for i, entry in enumerate(batch):
            row = i // COLS
            col = i % COLS
            mirrored_col = COLS - 1 - col
            draw_back(c, entry, row, mirrored_col)
        c.showPage()

    c.save()


def main() -> None:
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    os.makedirs(SITE_DATA_DIR, exist_ok=True)

    raw_entries = read_entries(COMPLETE_CSV)
    entries, duplicate_count = dedupe_entries(raw_entries)

    write_csv(entries)
    write_site_data(entries)
    write_pdf(entries)

    print(f"Input rows: {len(raw_entries)}")
    print(f"Duplicates removed/overwritten: {duplicate_count}")
    print(f"Complete unique words: {len(entries)}")
    print(f"Pages: {((len(entries) + CARDS_PER_SHEET - 1) // CARDS_PER_SHEET) * 2}")
    print(f"Wrote {COMPLETE_CSV}")
    print(f"Wrote {COMPLETE_PDF}")
    print(f"Updated {SITE_JSON}")
    print(f"Updated {SITE_JS}")


if __name__ == "__main__":
    main()
