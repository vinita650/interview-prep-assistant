import tomllib
import re
from pathlib import Path
from openai import OpenAI
from pypdf import PdfReader
import chromadb

# Read API key from secrets
script_dir = Path(__file__).parent
secrets_path = script_dir / '.streamlit' / 'secrets.toml'
with open(secrets_path, 'rb') as f:
    secrets = tomllib.load(f)
    api_key = secrets['OPENAI_API_KEY']

# Create OpenAI client
client = OpenAI(api_key=api_key)

# Find all PDFs in docs/
docs_dir = script_dir / 'docs'
pdf_files = sorted(docs_dir.glob('*.pdf'))

all_chunks = []
file_chunk_counts = {}

# Process each PDF
for pdf_path in pdf_files:
    pdf_name = pdf_path.name
    chunks = []

    try:
        pdf_reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"Warning: Failed to read {pdf_name}: {e}")
        continue

    # Process pages and create chunks
    chunk_id = 0

    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()

        # Skip if no text extracted
        if not text or not text.strip():
            continue

        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Skip empty pages after whitespace collapse
        if not text:
            continue

        # Split into chunks with overlap
        chunk_size = 1000
        overlap = 150
        step = chunk_size - overlap

        # Create chunks from this page
        for i in range(0, len(text), step):
            chunk_text = text[i:i + chunk_size]
            chunks.append({
                'text': chunk_text,
                'source': pdf_name,
                'page': page_num + 1,
                'id': f'{pdf_name}_{chunk_id}'
            })
            chunk_id += 1

            # Stop if we've covered the end of the text
            if i + chunk_size >= len(text):
                break

    if not chunks:
        print(f"Warning: {pdf_name} yielded no text")
        continue

    all_chunks.extend(chunks)
    file_chunk_counts[pdf_name] = len(chunks)
    print(f'{pdf_name}: {len(chunks)} chunks')

# Embed chunks in batches of 100
embeddings = []
for i in range(0, len(all_chunks), 100):
    batch = all_chunks[i:i + 100]
    batch_texts = [chunk['text'] for chunk in batch]

    response = client.embeddings.create(
        input=batch_texts,
        model='text-embedding-3-small'
    )

    for embedding in response.data:
        embeddings.append(embedding.embedding)

# Store in chromadb
chroma_path = script_dir / 'chroma_db'
client_chroma = chromadb.PersistentClient(path=str(chroma_path))
collection = client_chroma.get_or_create_collection(name='docs')

# Upsert to collection
documents = [chunk['text'] for chunk in all_chunks]
ids = [chunk['id'] for chunk in all_chunks]
metadatas = [{'source': chunk['source'], 'page': chunk['page']} for chunk in all_chunks]

collection.upsert(
    ids=ids,
    embeddings=embeddings,
    documents=documents,
    metadatas=metadatas
)

print(f"Total: {collection.count()} chunks in collection")
