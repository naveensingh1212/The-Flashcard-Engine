const BASE = import.meta.env.VITE_API_URL || "http://localhost:10000";

async function req(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  getDecks: () => req("/decks"),
  getDeck: (id) => req(`/decks/${id}`),
  deleteDeck: (id) => req(`/decks/${id}`, { method: "DELETE" }),
  uploadPDF: (file, deckName) => {
    const form = new FormData();
    form.append("file", file);
    if (deckName) form.append("deck_name", deckName);
    return req("/decks/upload", { method: "POST", body: form });
  },
  getStudySession: (deckId, limit = 20) =>
    req(`/decks/${deckId}/study?limit=${limit}`),
  reviewCard: (cardId, quality) =>
    req("/cards/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ card_id: cardId, quality }),
    }),
  getDeckStats: (deckId) => req(`/decks/${deckId}/stats`),
};