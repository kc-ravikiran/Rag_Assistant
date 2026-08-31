"""
Extend document_loaders to also handle plain .txt SOP files.
This patch is applied automatically when the loader is instantiated.
"""

from pathlib import Path
from typing import List
from langchain_core.documents import Document


def load_txt_sops(folder: Path) -> List[Document]:
    """Fallback: load .txt files as SOP documents when PDFs are unavailable."""
    docs = []
    for file in folder.glob("*.txt"):
        try:
            text = file.read_text(encoding="utf-8")
            # Split into ~1000-char chunks on double newlines
            sections = text.split("\n\n")
            buffer = ""
            for section in sections:
                buffer += section + "\n\n"
                if len(buffer) >= 800:
                    docs.append(Document(
                        page_content=buffer.strip(),
                        metadata={"source": str(file), "doc_type": "sop", "page": 0},
                    ))
                    buffer = ""
            if buffer.strip():
                docs.append(Document(
                    page_content=buffer.strip(),
                    metadata={"source": str(file), "doc_type": "sop", "page": 0},
                ))
        except Exception as e:
            print(f"⚠️  Could not load {file}: {e}")
    return docs
