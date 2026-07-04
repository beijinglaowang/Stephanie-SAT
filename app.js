const state = {
  cards: [],
  index: 0,
  flipped: false,
};

const elements = {
  card: document.querySelector("#card"),
  counter: document.querySelector("#counter"),
  progress: document.querySelector("#progress"),
  word: document.querySelector("#word"),
  definition: document.querySelector("#definition"),
  synonyms: document.querySelector("#synonyms"),
  antonyms: document.querySelector("#antonyms"),
  sentence: document.querySelector("#sentence"),
  root: document.querySelector("#root"),
  prev: document.querySelector("#prev"),
  next: document.querySelector("#next"),
};

const partOfSpeech = {
  adjective: "adj",
  noun: "n",
  verb: "v",
  adverb: "adv",
};

function normalizeCard(rawCard) {
  return {
    number: Number(rawCard.card_number),
    word: rawCard.word,
    pos: partOfSpeech[rawCard.part_of_speech] || rawCard.part_of_speech,
    definition: rawCard.definition,
    sentence: rawCard.sample_sentence,
    synonyms: rawCard.synonyms_top_3,
    antonyms: rawCard.antonyms_top_3,
    root: rawCard.root,
  };
}

function render() {
  const card = state.cards[state.index];
  if (!card) return;

  elements.word.textContent = card.word;
  elements.definition.textContent = `(${card.pos}) ${card.definition}`;
  elements.synonyms.textContent = card.synonyms;
  elements.antonyms.textContent = card.antonyms;
  elements.sentence.textContent = card.sentence;
  elements.root.textContent = card.root;
  elements.counter.textContent = `${state.index + 1} / ${state.cards.length}`;
  elements.progress.style.width = `${((state.index + 1) / state.cards.length) * 100}%`;
  elements.card.classList.toggle("is-flipped", state.flipped);
  document.title = `${card.word} - Stephanie SAT`;
}

function move(delta) {
  const total = state.cards.length;
  state.index = (state.index + delta + total) % total;
  state.flipped = false;
  render();
}

function flip() {
  state.flipped = !state.flipped;
  render();
}

elements.card.addEventListener("click", flip);
elements.prev.addEventListener("click", () => move(-1));
elements.next.addEventListener("click", () => move(1));

document.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft") move(-1);
  if (event.key === "ArrowRight") move(1);
  if (event.key === " " || event.key === "Enter") {
    if (document.activeElement === elements.prev || document.activeElement === elements.next) return;
    event.preventDefault();
    flip();
  }
});

if (Array.isArray(window.STEPHANIE_SAT_CARDS)) {
  state.cards = window.STEPHANIE_SAT_CARDS.map(normalizeCard);
  render();
} else {
  elements.word.textContent = "Cards unavailable";
  elements.definition.textContent = "Please refresh the page.";
}
