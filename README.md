Live app: (link coming)

# Interview prep assistant

It answers interview questions from my RAG and MCP cheat sheets, with page citations, and keeps a revision list of the topics I got wrong.

## How it works

- **Search tool over my PDFs:** `search_docs(query)` returns the 3 closest passages from the cheat sheets, with file and page, and the assistant cites them.
- **Action tools:** `save_weak_spot(topic, note)` adds a topic to `weak_spots.json` when I say I got something wrong, and `list_weak_spots()` returns the revision list when I ask what to revise.
- **Tool-call loop with a 5-round limit:** the model can call tools, see the results, and call again. After 5 rounds it stops and warns that the limit was reached.

## Run it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Put your key in `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "sk-..."
```

Then start the app:

```bash
streamlit run app.py
```

The source PDFs are not in the repo, but the index built from them is in `chroma_db/` (collection `docs`), so search works without rebuilding it.

## What I would build next

- Quiz mode
- A revision list that works online
- Login
- Voice
- v2: an RBI card rules assistant over my `handbook.pdf`
