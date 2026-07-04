# Stephanie SAT

A static GitHub Pages vocabulary flashcard app.

- Shows one SAT vocabulary card at a time.
- Click or tap the card to flip between the word and the back content.
- Swipe left/right or use the previous and next buttons to move through all 252 flashcards.
- Icon-only word lists are tracked per word.
- The `Switch` button moves the current word between the two lists.

The flashcard data is generated from `outputs/vocabulary_flashcards_complete_deduped_source.csv`.
The app loads `data/cards.js`; `data/cards.json` is kept as an inspectable source copy.
Shared state is stored in `data/state.json`.

To save across browsers, use the in-app `Setup sync` button and paste a fine-grained GitHub token with repository Contents read/write access for `beijinglaowang/Stephanie-SAT`. The token is stored only in that browser.
