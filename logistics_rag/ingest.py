"""
ingest.py
Run this script once (or whenever data changes) to build / refresh the vector store.

Usage:
    python ingest.py --api-key sk-...
    python ingest.py  # reads OPENAI_API_KEY from environment / .env
"""

import argparse
import os
import sys
from pathlib import Path

# Support .env files if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Patch document loader to also handle .txt SOPs
from src.document_loaders import LogisticsDocumentLoader
from src.txt_loader import load_txt_sops


def _patched_load_sops(self, folder: Path):
    """Load PDFs + .txt SOP files."""
    pdf_docs = LogisticsDocumentLoader._orig_load_sops(self, folder)
    txt_docs = load_txt_sops(folder)
    total = pdf_docs + txt_docs
    print(f"  📄 Loaded {len(total)} SOP chunks from {folder}")
    return total


LogisticsDocumentLoader._orig_load_sops = LogisticsDocumentLoader.load_sops
LogisticsDocumentLoader.load_sops = _patched_load_sops  # type: ignore


from src.rag_engine import LogisticsRAG


def main():
    parser = argparse.ArgumentParser(description="Ingest logistics documents into vector store")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"), help="OpenAI API key")
    parser.add_argument("--data-dir", default="./data", help="Path to data directory")
    parser.add_argument("--db-dir", default="./chroma_db", help="Vector store persistence directory")
    args = parser.parse_args()

    if not args.api_key:
        print("❌ OpenAI API key not found. Pass --api-key or set OPENAI_API_KEY.")
        sys.exit(1)

    print("🚀 Starting document ingestion...\n")
    rag = LogisticsRAG(openai_api_key=args.api_key, persist_dir=args.db_dir)
    counts = rag.ingest_documents(data_dir=args.data_dir)

    print("\n📊 Ingestion Summary:")
    for k, v in counts.items():
        print(f"   {k:<20} {v}")
    print("\n✅ Vector store saved to:", args.db_dir)
    print("   Run `python chat.py` to start querying.")


if __name__ == "__main__":
    main()
