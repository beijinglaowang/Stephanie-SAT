const GITHUB_STATE_URL = "https://api.github.com/repos/beijinglaowang/Stephanie-SAT/contents/data/state.json";
const LOCAL_STATE_KEY = "stephanieSatWordStates";
const TOKEN_KEY = "stephanieSatGithubToken";

const state = {
  cards: [],
  index: 0,
  mode: "unknown",
  flipped: false,
  wordStates: {},
  remoteSha: null,
  saveChain: Promise.resolve(),
  suppressClick: false,
  touchStart: null,
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
  go: document.querySelector("#go"),
  knownFilter: document.querySelector("#knownFilter"),
  unknownFilter: document.querySelector("#unknownFilter"),
  knownCount: document.querySelector("#knownCount"),
  unknownCount: document.querySelector("#unknownCount"),
  frontBadge: document.querySelector("#frontBadge"),
  backBadge: document.querySelector("#backBadge"),
  syncToggle: document.querySelector("#syncToggle"),
  syncPanel: document.querySelector("#syncPanel"),
  syncStatus: document.querySelector("#syncStatus"),
  syncToken: document.querySelector("#syncToken"),
  saveToken: document.querySelector("#saveToken"),
  clearToken: document.querySelector("#clearToken"),
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
    key: rawCard.word.toLowerCase(),
    pos: partOfSpeech[rawCard.part_of_speech] || rawCard.part_of_speech,
    definition: rawCard.definition,
    sentence: rawCard.sample_sentence,
    synonyms: rawCard.synonyms_top_3,
    antonyms: rawCard.antonyms_top_3,
    root: rawCard.root,
  };
}

function loadLocalStates() {
  try {
    const saved = JSON.parse(localStorage.getItem(LOCAL_STATE_KEY) || "{}");
    if (saved && typeof saved === "object") state.wordStates = saved;
  } catch {
    state.wordStates = {};
  }
}

function saveLocalStates() {
  localStorage.setItem(LOCAL_STATE_KEY, JSON.stringify(state.wordStates));
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

function setSyncStatus(text, kind = "") {
  elements.syncStatus.textContent = text;
  elements.syncToggle.classList.toggle("is-saving", kind === "saving");
  elements.syncToggle.classList.toggle("is-error", kind === "error");
}

function getWordState(card) {
  return state.wordStates[card.key] === 0 ? 0 : 1;
}

function setWordState(card, value) {
  state.wordStates[card.key] = value;
}

function cardsForMode() {
  return state.cards.filter((card) => (state.mode === "known" ? getWordState(card) === 0 : getWordState(card) === 1));
}

function currentCard() {
  return cardsForMode()[state.index] || null;
}

function countCards(value) {
  return state.cards.filter((card) => getWordState(card) === value).length;
}

function syncModeButtons() {
  elements.knownFilter.classList.toggle("is-active", state.mode === "known");
  elements.unknownFilter.classList.toggle("is-active", state.mode === "unknown");
}

function ensureValidIndex() {
  const list = cardsForMode();
  if (state.index >= list.length) state.index = Math.max(0, list.length - 1);
}

function renderEmpty() {
  const label = state.mode === "known" ? "Known" : "Unknown";
  elements.word.textContent = `No ${label} Words`;
  elements.definition.textContent = "";
  elements.synonyms.textContent = "";
  elements.antonyms.textContent = "";
  elements.sentence.textContent = "";
  elements.root.textContent = "";
  elements.counter.textContent = `0 / ${state.cards.length}`;
  elements.progress.style.width = "0%";
  elements.go.disabled = true;
  elements.card.classList.remove("is-flipped");
  elements.frontBadge.textContent = label;
  elements.backBadge.textContent = label;
}

function render() {
  ensureValidIndex();
  const list = cardsForMode();
  const card = list[state.index];
  elements.knownCount.textContent = countCards(0);
  elements.unknownCount.textContent = countCards(1);
  syncModeButtons();

  if (!card) {
    renderEmpty();
    return;
  }

  const known = getWordState(card) === 0;
  const stateLabel = known ? "Known" : "Unknown";
  elements.word.textContent = card.word;
  elements.definition.textContent = `(${card.pos}) ${card.definition}`;
  elements.synonyms.textContent = card.synonyms;
  elements.antonyms.textContent = card.antonyms;
  elements.sentence.textContent = card.sentence;
  elements.root.textContent = card.root;
  elements.counter.textContent = `${card.number} / ${state.cards.length}`;
  elements.progress.style.width = `${(card.number / state.cards.length) * 100}%`;
  elements.card.classList.toggle("is-flipped", state.flipped);
  elements.frontBadge.textContent = stateLabel;
  elements.backBadge.textContent = stateLabel;
  elements.frontBadge.classList.toggle("is-known", known);
  elements.backBadge.classList.toggle("is-known", known);
  elements.frontBadge.classList.toggle("is-unknown", !known);
  elements.backBadge.classList.toggle("is-unknown", !known);
  elements.go.disabled = false;
  document.title = `${card.word} - Stephanie SAT`;
}

function move(delta) {
  const total = cardsForMode().length;
  if (!total) return;
  state.index = (state.index + delta + total) % total;
  state.flipped = false;
  render();
}

function flip() {
  if (state.suppressClick) {
    state.suppressClick = false;
    return;
  }
  state.flipped = !state.flipped;
  render();
}

function switchMode(mode) {
  if (state.mode === mode) return;
  state.mode = mode;
  state.index = 0;
  state.flipped = false;
  render();
}

function mergeStates(incoming) {
  if (!incoming || typeof incoming !== "object") return;
  state.wordStates = { ...state.wordStates, ...incoming };
  saveLocalStates();
}

function decodeBase64Json(content) {
  const clean = content.replace(/\s/g, "");
  return JSON.parse(decodeURIComponent(Array.from(atob(clean), (char) => {
    return `%${char.charCodeAt(0).toString(16).padStart(2, "0")}`;
  }).join("")));
}

function encodeBase64Json(value) {
  const json = JSON.stringify(value, null, 2);
  return btoa(unescape(encodeURIComponent(json)));
}

async function loadRemoteStates() {
  setSyncStatus("Loading");
  try {
    const response = await fetch(`${GITHUB_STATE_URL}?t=${Date.now()}`, {
      headers: { Accept: "application/vnd.github+json" },
      cache: "no-store",
    });
    if (!response.ok) throw new Error("remote read failed");
    const payload = await response.json();
    const remote = decodeBase64Json(payload.content || "");
    state.remoteSha = payload.sha;
    mergeStates(remote.states);
    setSyncStatus(getToken() ? "Synced" : "Read only");
  } catch {
    setSyncStatus("Local", "error");
  }
  render();
}

async function refreshRemoteSha(mergeRemote = false) {
  const response = await fetch(`${GITHUB_STATE_URL}?t=${Date.now()}`, {
    headers: { Accept: "application/vnd.github+json" },
    cache: "no-store",
  });
  if (!response.ok) throw new Error("remote read failed");
  const payload = await response.json();
  state.remoteSha = payload.sha;
  if (mergeRemote) {
    const remote = decodeBase64Json(payload.content || "");
    mergeStates(remote.states);
  }
}

async function persistRemote(retry = true) {
  const token = getToken();
  if (!token) {
    setSyncStatus("Local", "error");
    return;
  }

  setSyncStatus("Saving", "saving");
  if (!state.remoteSha) await refreshRemoteSha();
  const body = {
    message: "Update SAT flashcard states",
    content: encodeBase64Json({
      version: 1,
      updatedAt: new Date().toISOString(),
      states: state.wordStates,
    }),
    branch: "main",
    sha: state.remoteSha,
  };

  const response = await fetch(GITHUB_STATE_URL, {
    method: "PUT",
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    if (response.status === 409 && retry) {
      await refreshRemoteSha();
      return persistRemote(false);
    }
    throw new Error("remote save failed");
  }
  const result = await response.json();
  state.remoteSha = result.content.sha;
  setSyncStatus("Synced");
}

function queueRemoteSave() {
  saveLocalStates();
  state.saveChain = state.saveChain
    .then(() => persistRemote())
    .catch(() => setSyncStatus("Local", "error"));
}

function toggleCurrentWord() {
  const card = currentCard();
  if (!card) return;
  setWordState(card, getWordState(card) === 0 ? 1 : 0);
  queueRemoteSave();
  if (!cardsForMode().includes(card)) {
    ensureValidIndex();
  }
  state.flipped = false;
  render();
}

function saveToken() {
  const token = elements.syncToken.value.trim();
  if (!token) return;
  localStorage.setItem(TOKEN_KEY, token);
  elements.syncToken.value = "";
  elements.syncPanel.hidden = true;
  queueRemoteSave();
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  elements.syncToken.value = "";
  setSyncStatus("Read only");
}

function handleTouchStart(event) {
  const touch = event.changedTouches[0];
  state.touchStart = { x: touch.clientX, y: touch.clientY };
}

function handleTouchEnd(event) {
  if (!state.touchStart) return;
  const touch = event.changedTouches[0];
  const dx = touch.clientX - state.touchStart.x;
  const dy = touch.clientY - state.touchStart.y;
  state.touchStart = null;
  if (Math.abs(dx) < 48 || Math.abs(dx) < Math.abs(dy) * 1.35) return;
  state.suppressClick = true;
  move(dx < 0 ? 1 : -1);
}

elements.card.addEventListener("click", flip);
elements.card.addEventListener("touchstart", handleTouchStart, { passive: true });
elements.card.addEventListener("touchend", handleTouchEnd, { passive: true });
elements.prev.addEventListener("click", () => move(-1));
elements.next.addEventListener("click", () => move(1));
elements.go.addEventListener("click", toggleCurrentWord);
elements.knownFilter.addEventListener("click", () => switchMode("known"));
elements.unknownFilter.addEventListener("click", () => switchMode("unknown"));
elements.syncToggle.addEventListener("click", () => {
  elements.syncPanel.hidden = !elements.syncPanel.hidden;
});
elements.saveToken.addEventListener("click", saveToken);
elements.clearToken.addEventListener("click", clearToken);

document.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft") move(-1);
  if (event.key === "ArrowRight") move(1);
  if (event.key.toLowerCase() === "g") toggleCurrentWord();
  if (event.key === " " || event.key === "Enter") {
    if ([elements.prev, elements.next, elements.go, elements.knownFilter, elements.unknownFilter].includes(document.activeElement)) return;
    event.preventDefault();
    flip();
  }
});

document.addEventListener("visibilitychange", () => {
  if (!document.hidden) loadRemoteStates();
});

if (Array.isArray(window.STEPHANIE_SAT_CARDS)) {
  state.cards = window.STEPHANIE_SAT_CARDS.map(normalizeCard);
  loadLocalStates();
  render();
  loadRemoteStates();
} else {
  elements.word.textContent = "Cards unavailable";
  elements.definition.textContent = "Please refresh the page.";
}
