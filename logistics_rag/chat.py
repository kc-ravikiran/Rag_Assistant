"""
chat.py
Interactive CLI chat for the Logistics RAG system.

Usage:
    python chat.py --api-key sk-...
    python chat.py              # reads OPENAI_API_KEY from environment / .env
"""

import argparse
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Patch txt SOP loader (same as ingest.py)
from src.document_loaders import LogisticsDocumentLoader
from src.txt_loader import load_txt_sops
from pathlib import Path


def _patched_load_sops(self, folder: Path):
    pdf_docs = LogisticsDocumentLoader._orig_load_sops(self, folder)
    txt_docs = load_txt_sops(folder)
    return pdf_docs + txt_docs


LogisticsDocumentLoader._orig_load_sops = LogisticsDocumentLoader.load_sops
LogisticsDocumentLoader.load_sops = _patched_load_sops  # type: ignore

from src.rag_engine import LogisticsRAG
from src.query_router import QueryRouter


BANNER = """
╔══════════════════════════════════════════════════════╗
║    🚚  Logistics Delivery Manager — RAG Assistant    ║
╠══════════════════════════════════════════════════════╣
║  Ask about: shipment delays, SLA breaches,           ║
║  driver performance, routes, or SOPs.                ║
║  Type 'quit' or 'exit' to stop.                      ║
║  Type 'sources' after a query to see source docs.    ║
╚══════════════════════════════════════════════════════╝
"""

SAMPLE_QUERIES = [
    "Which shipments are delayed by more than 60 minutes?",
    "How many SLA breaches occurred in the North zone?",
    "Which driver has the most delayed deliveries?",
    "What is the SOP for handling failed deliveries?",
    "List all shipments with SLA status 'Breached'.",
    "What is the on-time delivery rate for driver Ravi Kumar?",
    "Which route has the highest delay rate?",
]


def main():
    parser = argparse.ArgumentParser(description="Chat with the Logistics RAG assistant")
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"))
    parser.add_argument("--db-dir", default="./chroma_db")
    parser.add_argument("--data-dir", default="./data", help="Re-ingest data on startup if db missing")
    args = parser.parse_args()

    if not args.api_key:
        print("❌ OpenAI API key not found. Pass --api-key or set OPENAI_API_KEY.")
        sys.exit(1)

    print(BANNER)
    router = QueryRouter()
    rag = LogisticsRAG(openai_api_key=args.api_key, persist_dir=args.db_dir)

    # Auto-ingest if vector store doesn't exist
    if not os.path.exists(args.db_dir) or not os.listdir(args.db_dir):
        print("ℹ️  No vector store found. Ingesting documents first...\n")
        rag.ingest_documents(data_dir=args.data_dir)
    else:
        rag.load_existing_vectorstore()

    rag.build_chain()

    print("\n💡 Sample queries you can try:")
    for i, q in enumerate(SAMPLE_QUERIES, 1):
        print(f"   {i}. {q}")
    print()

    last_result = None

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye! 👋")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit"):
            print("Goodbye! 👋")
            break

        if user_input.lower() == "sources" and last_result:
            print("\n📚 Sources used in last answer:")
            for i, s in enumerate(last_result["sources"], 1):
                print(f"  [{i}] {s['doc_type'].upper()} | {s['source']}")
                if s.get("page"):
                    print(f"       Page: {s['page']}")
                print(f"       …{s['snippet']}…")
            print()
            continue

        try:
            result = rag.query(user_input)
            last_result = result
            intent_label = router.get_intent_label(result["intent"])
            print(f"\n{intent_label}")
            print(f"\nAssistant: {result['answer']}")
            print(f"\n  ({len(result['sources'])} source chunks retrieved. Type 'sources' to inspect.)\n")

        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    main()
