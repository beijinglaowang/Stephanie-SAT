# Stephanie SAT

A static GitHub Pages vocabulary flashcard app.

- Shows one SAT vocabulary card at a time.
- Click or tap the card to flip between the word and the back content.
- Swipe left/right or use the previous and next buttons to move through all 263 flashcards.
- Known and Unknown lists are tracked per word.
- The Go button moves the current word between Known and Unknown.

The flashcard data is generated from `outputs/vocabulary_flashcards_duplex_10cards_full_a4_source.csv`.
The app loads `data/cards.js`; `data/cards.json` is kept as an inspectable source copy.
Shared state is stored in `data/state.json`.
