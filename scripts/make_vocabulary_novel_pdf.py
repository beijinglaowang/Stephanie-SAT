from __future__ import annotations

import html
import os
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "artifacts" / "vocabulary_fiction_novel.md"
PDF_PATH = ROOT / "artifacts" / "vocabulary_fiction_novel.pdf"


def markdown_inline_to_reportlab(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
    return text


def has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u9fff]", text))


def flush_paragraph(story, paragraph_lines, body_style, cjk_body_style):
    if not paragraph_lines:
        return
    text = " ".join(line.strip() for line in paragraph_lines)
    style = cjk_body_style if has_cjk(text) else body_style
    story.append(Paragraph(markdown_inline_to_reportlab(text), style))
    story.append(Spacer(1, 0.11 * inch))
    paragraph_lines.clear()


def build_pdf() -> None:
    os.makedirs(PDF_PATH.parent, exist_ok=True)
    md_text = MD_PATH.read_text(encoding="utf-8")
    first_title = next((line[2:].strip() for line in md_text.splitlines() if line.startswith("# ")), "Vocabulary Fiction Novel")
    cjk_font = "STSong-Light"
    cjk_bold_font = "STSong-Light"
    yahei = Path("C:/Windows/Fonts/msyh.ttc")
    yahei_bold = Path("C:/Windows/Fonts/msyhbd.ttc")
    if yahei.exists():
        pdfmetrics.registerFont(TTFont("MicrosoftYaHei", str(yahei)))
        cjk_font = "MicrosoftYaHei"
        cjk_bold_font = "MicrosoftYaHei"
        if yahei_bold.exists():
            pdfmetrics.registerFont(TTFont("MicrosoftYaHei-Bold", str(yahei_bold)))
            cjk_bold_font = "MicrosoftYaHei-Bold"
    else:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "NovelBody",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=10.7,
        leading=14.1,
        firstLineIndent=16,
        spaceAfter=2,
    )
    title = ParagraphStyle(
        "NovelTitle",
        parent=styles["Title"],
        fontName="Times-Bold",
        fontSize=26,
        leading=31,
        alignment=1,
        textColor=colors.HexColor("#111418"),
        spaceAfter=14,
    )
    subtitle = ParagraphStyle(
        "NovelSubtitle",
        parent=body,
        fontName="Times-Italic",
        fontSize=11,
        leading=14,
        alignment=1,
        firstLineIndent=0,
        textColor=colors.HexColor("#4C5563"),
        spaceAfter=22,
    )
    chapter = ParagraphStyle(
        "NovelChapter",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#111418"),
        spaceBefore=8,
        spaceAfter=10,
    )
    cjk_body = ParagraphStyle(
        "NovelChineseBody",
        parent=body,
        fontName=cjk_font,
        fontSize=10.8,
        leading=15.8,
        firstLineIndent=18,
    )
    cjk_title = ParagraphStyle(
        "NovelChineseTitle",
        parent=title,
        fontName=cjk_bold_font,
        fontSize=23,
        leading=29,
    )
    cjk_subtitle = ParagraphStyle(
        "NovelChineseSubtitle",
        parent=subtitle,
        fontName=cjk_font,
        fontSize=10.8,
        leading=15,
    )
    cjk_chapter = ParagraphStyle(
        "NovelChineseChapter",
        parent=chapter,
        fontName=cjk_bold_font,
        fontSize=15,
        leading=20,
    )

    story = []
    paragraph_lines: list[str] = []
    first_chapter = True
    first_title_seen = False

    for raw_line in md_text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("# "):
            flush_paragraph(story, paragraph_lines, body, cjk_body)
            if first_title_seen:
                story.append(PageBreak())
                first_chapter = True
            first_title_seen = True
            style = cjk_title if has_cjk(line) else title
            story.append(Paragraph(markdown_inline_to_reportlab(line[2:]), style))
        elif line.startswith("## "):
            flush_paragraph(story, paragraph_lines, body, cjk_body)
            if first_chapter:
                first_chapter = False
            else:
                story.append(PageBreak())
            style = cjk_chapter if has_cjk(line) else chapter
            story.append(Paragraph(markdown_inline_to_reportlab(line[3:]), style))
        elif line.startswith("_") and line.endswith("_") and not paragraph_lines:
            style = cjk_subtitle if has_cjk(line) else subtitle
            subtitle_text = line.strip("_") if has_cjk(line) else line
            story.append(Paragraph(markdown_inline_to_reportlab(subtitle_text), style))
        elif not line:
            flush_paragraph(story, paragraph_lines, body, cjk_body)
        else:
            paragraph_lines.append(line)
    flush_paragraph(story, paragraph_lines, body, cjk_body)

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        rightMargin=0.72 * inch,
        leftMargin=0.72 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.72 * inch,
        title=first_title,
        author="Codex",
    )
    doc.build(story)
    print(PDF_PATH)


if __name__ == "__main__":
    build_pdf()
