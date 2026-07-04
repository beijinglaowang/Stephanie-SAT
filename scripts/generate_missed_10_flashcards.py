from __future__ import annotations

import csv
import os
from dataclasses import dataclass

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(ROOT, "outputs")
PDF_PATH = os.path.join(OUTPUT_DIR, "missed_10_flashcards_duplex_a4.pdf")
CSV_PATH = os.path.join(OUTPUT_DIR, "missed_10_flashcards_duplex_a4_source.csv")

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


@dataclass(frozen=True)
class Entry:
    word: str
    pos: str
    definition: str
    sentence: str
    synonyms: str
    antonyms: str
    root: str


ENTRIES = [
    Entry(
        "Strenuous",
        "adj",
        "vigorous; marked by energy and stamina",
        "The strenuous hike left everyone exhausted but proud.",
        "difficult, arduous, tough",
        "effortless, easy, simple",
        "Latin strenuus, active or brisk.",
    ),
    Entry(
        "Zenith",
        "n",
        "the highest point of something",
        "Her career reached its zenith after the award.",
        "height, high point, peak",
        "bottom, base, nadir",
        "Arabic samt, path or direction, source of zenith.",
    ),
    Entry(
        "Tenacious",
        "adj",
        "aggressively persistent at something",
        "The tenacious lawyer kept asking questions until the truth emerged.",
        "firm, tight, strong",
        "loose, weak, yielding",
        "Latin tenax/tenere, holding fast.",
    ),
    Entry(
        "Scintillating",
        "adj",
        "brilliant; lively; stimulating; witty",
        "The guest gave a scintillating speech that made the room laugh.",
        "sparkling, shining, bright",
        "dull, boring, matte",
        "Latin scintilla, spark.",
    ),
    Entry(
        "Salient",
        "adj",
        "prominent; of notable significance",
        "The report highlighted the salient points before the meeting.",
        "important, major, principal",
        "inconspicuous, insignificant, unimportant",
        "Latin salire, to leap or jump.",
    ),
    Entry(
        "Supercilious",
        "adj",
        "aloof and superior",
        "His supercilious tone made the new students uncomfortable.",
        "arrogant, haughty, snobbish",
        "humble, modest, respectful",
        "Latin supercilium, eyebrow; linked to raised-eyebrow pride.",
    ),
    Entry(
        "Tenuous",
        "adj",
        "flimsy; weak; of little substance",
        "The argument was tenuous because it relied on guesses.",
        "fragile, weak, flimsy",
        "strong, thick, substantial",
        "Latin tenuis, thin or slender.",
    ),
    Entry(
        "Truncate",
        "v",
        "to shorten, often by cutting off",
        "The editor had to truncate the article to fit the page.",
        "cut, pare, reduce",
        "lengthen, extend, expand",
        "Latin truncare, to cut off or maim.",
    ),
    Entry(
        "Serendipity",
        "n",
        "luck; finding good things you were not even looking for",
        "By serendipity, we found the perfect cafe while lost.",
        "good luck, chance, coincidence",
        "mishap, bad luck, misfortune",
        "Coined from Serendip, old name for Sri Lanka.",
    ),
    Entry(
        "Venerable",
        "adj",
        "respectable because of age or achievements",
        "The venerable professor still advised young scientists.",
        "respected, revered, honored",
        "dishonorable, disreputable, irreverent",
        "Latin venerari, to worship or revere.",
    ),
]


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


def draw_ruled_field(
    c: canvas.Canvas,
    label: str,
    text: str,
    x: float,
    y: float,
    width: float,
    row_h: float,
    max_lines: int,
    body_size: float = 8.4,
) -> float:
    label_w = 50
    text_x = x + label_w
    text_w = width - label_w
    line_y = y - row_h + 5.5

    c.setStrokeColor(colors.HexColor("#8E98A6"))
    c.setLineWidth(0.45)
    c.line(x, line_y, x + width, line_y)

    c.setFillColor(colors.HexColor("#5B5F66"))
    c.setFont("Helvetica-Bold", 7.8)
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

    definition = f"({entry.pos}) {entry.definition}"
    c.setFillColor(colors.HexColor("#111418"))
    c.setFont("Helvetica-Bold", 10.1)
    line_y = inner_y - 14
    for line in limited_lines(definition, "Helvetica-Bold", 10.1, inner_w, 3):
        c.drawCentredString(inner_x + inner_w / 2, line_y, line)
        line_y -= 11.0

    c.setStrokeColor(colors.HexColor("#9099A6"))
    c.setLineWidth(0.45)
    c.line(inner_x, line_y + 4, inner_x + inner_w, line_y + 4)

    body_y = line_y - 6
    body_y = draw_ruled_field(c, "Synonym", entry.synonyms, inner_x, body_y, inner_w, 20, 2, 8.4)
    body_y = draw_ruled_field(c, "Antonym", entry.antonyms, inner_x, body_y, inner_w, 20, 2, 8.4)
    body_y = draw_ruled_field(c, "Sentence", entry.sentence, inner_x, body_y, inner_w, 36, 3, 8.1)
    draw_ruled_field(c, "Root", entry.root, inner_x, body_y, inner_w, 28, 2, 8.1)


def make_csv() -> None:
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
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
        for i, entry in enumerate(ENTRIES, start=1):
            writer.writerow([
                i,
                entry.word,
                entry.pos,
                entry.definition,
                entry.sentence,
                entry.synonyms,
                entry.antonyms,
                entry.root,
            ])


def make_pdf() -> None:
    c = canvas.Canvas(PDF_PATH, pagesize=A4)

    draw_cut_guides(c)
    for i, entry in enumerate(ENTRIES):
        row = i // COLS
        col = i % COLS
        draw_front(c, entry, row, col)
    c.showPage()

    # Long-edge duplex printing mirrors the physical back side horizontally.
    draw_cut_guides(c, "back")
    for i, entry in enumerate(ENTRIES):
        row = i // COLS
        col = i % COLS
        mirrored_col = COLS - 1 - col
        draw_back(c, entry, row, mirrored_col)
    c.showPage()

    c.save()


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    make_csv()
    make_pdf()
    print(f"Cards: {len(ENTRIES)}")
    print(f"Pages: 2")
    print(f"Card size cm: {CARD_W / 28.3464567:.2f} x {CARD_H / 28.3464567:.2f}")
    print(f"Wrote {PDF_PATH}")
    print(f"Wrote {CSV_PATH}")


if __name__ == "__main__":
    main()
