from pathlib import Path


PROJECT_STRUCTURE = {
    "data/raw/.gitkeep": "",
    "data/processed/.gitkeep": "",
    "data/chroma_db/.gitkeep": "",

    "src/__init__.py": "",

    "src/config.py": '''# Project configuration

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHROMA_PATH = "data/chroma_db"

TOP_K = 5
''',

    "src/ingestion.py": '''"""
PDF ingestion module.

Responsible for:
- Loading PDF files
- Extracting text
- Preserving page numbers
"""

# TODO: Implement PDF extraction
''',

    "src/chunking.py": '''"""
Section-aware chunking module.

Responsible for:
- Detecting sections
- Creating section-aware chunks
- Attaching metadata
"""

# TODO: Implement chunking
''',

    "src/embeddings.py": '''"""
Embedding module.

Responsible for:
- Loading HuggingFace embedding model
- Generating embeddings
"""

# TODO: Implement embeddings
''',

    "src/vector_store.py": '''"""
Vector store module.

Responsible for:
- Creating ChromaDB
- Indexing chunks
- Loading existing vector store
"""

# TODO: Implement ChromaDB
''',

    "src/retrieval.py": '''"""
Retrieval module.

Responsible for:
- Receiving clinical queries
- Retrieving relevant chunks
- Returning metadata and sources
"""

# TODO: Implement retrieval
''',

    "evaluation/clinical_queries.json": '''[
    {
        "id": 1,
        "query": "What are the recommended HbA1c targets for adults with type 2 diabetes?"
    },
    {
        "id": 2,
        "query": "What lifestyle interventions are recommended for people with type 2 diabetes?"
    },
    {
        "id": 3,
        "query": "What is the recommended initial pharmacological treatment?"
    },
    {
        "id": 4,
        "query": "When should treatment be intensified?"
    },
    {
        "id": 5,
        "query": "When should an SGLT2 inhibitor be considered?"
    },
    {
        "id": 6,
        "query": "What are the recommendations for patients with chronic kidney disease?"
    },
    {
        "id": 7,
        "query": "What are the recommendations for patients with cardiovascular disease?"
    },
    {
        "id": 8,
        "query": "How should blood glucose control be monitored?"
    }
]
''',

    "docs/sources.md": '''# Clinical RAG Sources

## Source 1 — NICE

- Organization: NICE
- Guideline: NG28
- Title: Type 2 diabetes in adults: management
- Official URL: https://www.nice.org.uk/guidance/ng28
- Credibility:
- Public accessibility:

## Source 2 — WHO

- Organization: World Health Organization
- Guideline: HEARTS-D
- Title: Diagnosis and management of type 2 diabetes
- Official URL: https://www.who.int/publications/i/item/who-ucn-ncd-20.1
- Credibility:
- Public accessibility:
''',

    "app.py": '''"""
Main application / integration entry point.

Today's pipeline:

PDF
    ↓
Ingestion
    ↓
Chunking
    ↓
Embeddings
    ↓
ChromaDB
    ↓
Retrieval
"""

def main():
    print("Clinical RAG System")
    print("-------------------")
    print("Pipeline is ready for implementation.")


if __name__ == "__main__":
    main()
''',

    "requirements.txt": '''PyMuPDF
langchain
langchain-community
langchain-huggingface
chromadb
sentence-transformers
''',

    ".gitignore": '''venv/
.venv/
__pycache__/
*.pyc
.env

# Raw PDFs
data/raw/*.pdf

# Vector database
data/chroma_db/*

# Python cache
.ipynb_checkpoints/
'''
}


def create_project_structure():
    created = 0
    skipped = 0

    for file_path, content in PROJECT_STRUCTURE.items():

        path = Path(file_path)

        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            print(f"[SKIP] {path}")
            skipped += 1
            continue

        path.write_text(content, encoding="utf-8")

        print(f"[CREATE] {path}")
        created += 1

    print("\n" + "=" * 50)
    print("Project structure created successfully!")
    print(f"Created: {created}")
    print(f"Skipped: {skipped}")
    print("=" * 50)


if __name__ == "__main__":
    create_project_structure()