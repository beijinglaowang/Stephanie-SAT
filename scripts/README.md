# Generation Scripts

These scripts preserve the vocabulary build process in the GitHub repo.

- `generate_flashcards_from_final_csv.py` regenerates the final duplex A4 flashcard PDF from `artifacts/vocabulary_flashcards_complete_deduped_source.csv` and refreshes `data/cards.json` plus `data/cards.js`.
- `make_vocabulary_novel_pdf.py` regenerates `artifacts/vocabulary_fiction_novel.pdf` from `artifacts/vocabulary_fiction_novel.md`.
- `update_vocabulary_novel_family_bilingual.py` applies the latest family-role story update and appends the Chinese version.

The historical scripts are kept because they were part of creating the final card set.

Run scripts from the repository root with Python and `reportlab` installed.
