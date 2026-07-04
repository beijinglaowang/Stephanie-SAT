# Stephanie SAT

A static GitHub Pages vocabulary flashcard app.

- Shows one SAT vocabulary card at a time.
- Click or tap the card to flip between the word and the back content.
- Swipe left/right or use the previous and next buttons to move through all 252 flashcards.
- Icon-only word lists are tracked per word.
- The `Switch` button moves the current word between the two lists.

The flashcard data is generated from `artifacts/vocabulary_flashcards_complete_deduped_source.csv`.
The app loads `data/cards.js`; `data/cards.json` is kept as an inspectable source copy.
Shared state is stored in `data/state.json`.

## Committed study artifacts

Final generated records are committed in `artifacts/`:

- `artifacts/vocabulary_flashcards_complete_deduped_source.csv`
- `artifacts/vocabulary_flashcards_complete_deduped.pdf`
- `artifacts/vocabulary_fiction_novel.md`
- `artifacts/vocabulary_fiction_novel.pdf`

Generation and update scripts are committed in `scripts/`. The repo-native
generators are:

- `scripts/generate_flashcards_from_final_csv.py`
- `scripts/make_vocabulary_novel_pdf.py`

Both scripts use `artifacts/` as their source/output folder.

To save across browsers, use the in-app `Setup sync` button and paste a fine-grained GitHub token with repository Contents read/write access for `beijinglaowang/Stephanie-SAT`. The token is stored only in that browser.
