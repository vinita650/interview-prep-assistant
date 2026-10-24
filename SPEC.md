# My capstone

In one sentence: It answers interview questions from my RAG and MCP cheat sheets, with page citations, and keeps a revision list of the topics I got wrong.

Documents (PDFs in docs/, fine to make public): RAG-Interview-Cheat-Sheet.pdf, MCP-Cheat-Sheet.pdf

Tool 1: search_docs(query), returns the 3 closest passages with file and page. Use it when: any question about RAG, MCP or AI engineering.
Tool 2: save_weak_spot(topic, note), adds a topic to weak_spots.json. Use it when: I say I got something wrong or want to revise it.
Tool 3: list_weak_spots(), returns the revision list. Use it when: I ask what to revise.

Test questions:
- knowledge: What is lost in the middle, and why does it matter for RAG?
- action: I got that wrong in a mock interview. Add it to my revision list.
- follow-up: What should I revise?
- small talk (no tool should fire): Hi, how is your day going?

Not in v1 (parking lot): quiz mode, a revision list that works online, login, voice. v2: RBI card rules assistant over my handbook.pdf.

Stack: Python, OpenAI gpt-5.4-mini for chat, text-embedding-3-small for embeddings,
Chroma in ./chroma_db (collection "docs"), Streamlit chat UI,
key read with st.secrets from .streamlit/secrets.toml. Build every file path from the script's own folder.