from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "artifacts" / "vocabulary_fiction_novel.md"
CSV_PATH = ROOT / "artifacts" / "vocabulary_flashcards_complete_deduped_source.csv"


NEW_TITLE = "# Stephanie and the Riverlight Edict"
NEW_SUBTITLE = (
    "_A study novella using every unique word from the complete deduped "
    "flashcard set. Vocabulary words are bolded at first use._"
)

NEW_WORD_SCENE = """Years earlier, Stephanie's **venerable** Grandma Ada and Grandpa Bruce had taught her the **salient** rule of lenses: every beam reveals the hand that blocks it. Bruce had a **tenacious** faith in hidden rivers, but his proof was **tenuous**; Ada had to **truncate** every lesson whenever Council inspectors passed. By **serendipity**, Stephanie still owned one page from his notebook, a diagram with a **scintillating** blue arc. When a **supercilious** inspector dismissed it as childish, she kept it under her mattress until the city's lies reached their **zenith**."""


def replace_once(text: str, old: str, new: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    return text


def recast_story(text: str) -> str:
    text = replace_once(text, "# The Refraction Edict", NEW_TITLE)
    text = re.sub(r"_A study novella using every unique word from the flashcard set\. Vocabulary words are bolded at first use\._", NEW_SUBTITLE, text)

    if "**zenith**" not in text.lower():
        marker = "The first strange sign arrived as an **aberration** in a lens: a thin blue flame bending the wrong way through clear glass. Her master called it dust. Liora knew dust did not sing."
        text = replace_once(text, marker, marker + "\n\n" + NEW_WORD_SCENE)

    special_replacements = [
        (
            "At the edge waited an old woman in a blue coat.",
            "At the edge waited Stephanie's grandmother, Ada Dain, in a blue coat.",
        ),
        (
            '"Sella Dain. Once an **eminent** engineer. Now a heretic, according to **edict** seven hundred and nine."',
            '"Grandma Ada," Stephanie whispered. "My grandmother."\n\nAda lifted her chin. "Once an **eminent** engineer. Now a heretic, according to **edict** seven hundred and nine."',
        ),
        (
            "At last they found Mara's brother, Tavin, in a cell marked _dangerous_. He was not dangerous. He was **forlorn**, feverish, and holding a cracked lens.",
            "At last they found Stephanie's grandfather, Bruce, in a cell marked _dangerous_. Grandpa Bruce was not dangerous. He was **forlorn**, feverish, and holding a cracked lens.",
        ),
        (
            '"Obviously," Mara said, too **coy** to cry.',
            '"Obviously," Stephanie said, too **coy** to cry.',
        ),
        (
            "Mara touched his hair with sudden tenderness.",
            "Stephanie touched Grandpa Bruce's hand with sudden tenderness.",
        ),
        (
            "Vey remembered the Kest family. Stubborn, poor, **obstinate**. The brother had refused to **repudiate** his engineering notes even under punishment.",
            "Vey remembered the Kest family, then Stephanie's grandfather. Stubborn, poor, **obstinate**. Grandpa Bruce had refused to **repudiate** his engineering notes even under punishment.",
        ),
        (
            "At the central chamber, they found the ring mounted above a dry fountain. Around it were names of the first engineers, including Sella's grandmother, the **epitome** of the old guild's **prowess**.",
            "At the central chamber, they found the ring mounted above a dry fountain. Around it were names of the first engineers, including Ada's grandmother, the **epitome** of the old guild's **prowess**.",
        ),
        (
            "Their guide was a **taciturn** prisoner named Nox, thin and **pallid**, with eyes like sharpened slate. He had once written a **periodical** mocking the Council's **ostentatious** charity balls.",
            "Their guide was a **taciturn** prisoner named Jimin, thin and **pallid**, with eyes like sharpened slate. She had once written a **periodical** mocking the Council's **ostentatious** charity balls.",
        ),
        (
            "Melissa's face changed. The **bashful** bravado left it. \"My brother is in the Bell House.\"",
            "Melissa's face changed. The **bashful** bravado left it. \"Jimin is in the Bell House. She owes me three figs and a rescue.\"",
        ),
        (
            "\"My brother first. Figs later.\"",
            "\"Rescue first. Figs later.\"",
        ),
        (
            "For that **temerity**, he had been made to copy water ledgers until his fingers bled.",
            "For that **temerity**, she had been made to copy water ledgers until her fingers bled.",
        ),
        (
            '"Mara Kest," he said. "You still owe me three figs."',
            '"Melissa Kest," she said. "You still owe me three figs."',
        ),
        (
            "Vey offered him mercy if he would **concede** that the river maps were false.",
            "Vey offered her mercy if she would **concede** that the river maps were false.",
        ),
        (
            "The nurse, Iven, was **magnanimous** even in exhaustion. He ran a **philanthropic** clinic with no patron except stubborn decency.",
            "The nurse, Grace, was **magnanimous** even in exhaustion. She ran a **philanthropic** clinic with no patron except stubborn decency.",
        ),
        (
            "She ran a **philanthropic** clinic with no patron except stubborn decency. His waiting room was a **morass** of fever, dust, and whispered complaints.",
            "She ran a **philanthropic** clinic with no patron except stubborn decency. Her waiting room was a **morass** of fever, dust, and whispered complaints.",
        ),
        (
            "Then Jimin appeared on the Hall steps. Grandma Ada had freed him during the confusion.",
            "Then Jimin appeared on the Hall steps. Grandma Ada had freed her during the confusion.",
        ),
    ]
    for old, new in special_replacements:
        text = text.replace(old, new)

    replacements = [
        ("Liora's", "Stephanie's"),
        ("Liora", "Stephanie"),
        ("Mara's", "Melissa's"),
        ("Mara Kest", "Melissa Kest"),
        ("Mara", "Melissa"),
        ("Jorin's", "Brandon's"),
        ("Jorin", "Brandon"),
        ("Sella's", "Grandma Ada's"),
        ("Sella", "Grandma Ada"),
        ("Tavin's", "Grandpa Bruce's"),
        ("Tavin", "Grandpa Bruce"),
        ("Pell's", "Yamin's"),
        ("Pell", "Yamin"),
        ("Nox's", "Jimin's"),
        ("Nox", "Jimin"),
        ("Iven's", "Grace's"),
        ("Iven", "Grace"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)

    return text


def validate(text: str) -> None:
    with CSV_PATH.open(encoding="utf-8-sig", newline="") as handle:
        words = [row["word"] for row in csv.DictReader(handle)]

    missing = [
        word
        for word in words
        if not re.search(r"\b" + re.escape(word) + r"\b", text, flags=re.IGNORECASE)
    ]
    required_names = ["Stephanie", "Brandon", "Melissa", "Jimin", "Ada", "Grace", "Bruce", "Yamin", "Grandma Ada", "Grandpa Bruce"]
    missing_names = [name for name in required_names if name not in text]

    if missing:
        raise SystemExit(f"Missing vocabulary words: {missing}")
    if missing_names:
        raise SystemExit(f"Missing character names: {missing_names}")


def main() -> None:
    text = MD_PATH.read_text(encoding="utf-8")
    text = recast_story(text)
    validate(text)
    MD_PATH.write_text(text, encoding="utf-8", newline="\n")
    print(MD_PATH)


if __name__ == "__main__":
    main()
