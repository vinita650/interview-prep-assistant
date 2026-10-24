# Test log: Interview Prep Assistant (v1)

Run date: 2026-10-24. Model: gpt-5.4-mini. Every question below was sent through the Streamlit chat UI in a fresh browser page, and the answers are copied from that run. The app runs from a scratch copy so the revision list in the project folder was not changed by the test. Screenshots are in `screenshots/`.

Pass means: the expected tool fired (or none did for small talk) and the answer matched the spec.

## Results

| # | Type | Question | Tool(s) that fired | Answer (short) | Result |
|---|------|----------|--------------------|----------------|--------|
| 1 | Knowledge | What is lost in the middle, and why does it matter for RAG? | `search_docs` | Explains the attention pattern and cites `[RAG-Interview-Cheat-Sheet.pdf p.15]` | Pass |
| 2 | Knowledge | What is the difference between MCP tools and MCP resources? | `search_docs` ×2 | Tools are model-triggered actions; resources are read-only data by URI. Cites `[MCP-Cheat-Sheet.pdf p.11]` | Pass |
| 3 | Knowledge | Can you explain what a vector database does in a RAG pipeline? | `search_docs` | Stores embeddings, does nearest-neighbour search; cites p.6 and p.14 | Pass |
| 4 | Action | I mixed up stdio and SSE transports in a mock interview. Add it to my revision list. | `save_weak_spot(topic="stdio vs SSE transports", note=...)` | "Added to your revision list: stdio vs SSE transports." | Pass |
| 5 | Follow-up | What should I revise? | `list_weak_spots` | Lists both saved topics with their notes | Pass |
| 6 | Unanswerable | What is the RBI credit card late payment fee limit? | `search_docs` (no strong match) | "I don't have a strong match in my notes for that." No guessed figure | Pass |
| 7 | Unanswerable | What is the current stock price of Apple? | None | "I don't have a strong match in my notes for that." No guessed price | Pass |
| 8 | Small talk | Good morning! Nice to meet you. | None | "Good morning! Nice to meet you too." | Pass |

Tool coverage: `search_docs` (q1–3, q6), `save_weak_spot` (q4), `list_weak_spots` (q5). All three tools fired at least once, and small talk fired none.

## Earlier run

A first pass with an extra small-talk question ("Hi, how is your day going?") and a different "lost in the middle" question gave the same tool behaviour. The answers were worded differently and the citation page changed (p.8 in that run, p.15 in this one).

## Known issues

- **Citation pages vary between runs.** The same passage was cited as p.8 in one run and p.15 in another. The retrieved text is the same; the model picks which page to cite. This is worth checking before the demo.
- **Saves are not de-duplicated.** Saving the same topic twice adds it twice to `weak_spots.json`.
- **Off-topic questions are not always refused by the same wording.** The "stock price" answer in the first pass said it could not look up live data. In this run it used the spec's "no strong match" line. Both avoided guessing, but only the spec's wording is a clean pass.
- **Search queries are rewritten by the model.** The 🔧 line shows the rewritten query, not the question the user typed. That is expected, but it can look odd in a screenshot.
