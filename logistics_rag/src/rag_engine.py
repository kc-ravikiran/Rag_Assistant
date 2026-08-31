"""
Logistics RAG Engine
Core retrieval-augmented generation pipeline for Delivery Manager queries.
"""

import os
from typing import List, Dict, Any
from pathlib import Path

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document

try:
    from .document_loaders import LogisticsDocumentLoader
    from .query_router import QueryRouter
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.document_loaders import LogisticsDocumentLoader
    from src.query_router import QueryRouter


SYSTEM_PROMPT = """You are an intelligent assistant for a Delivery Manager in a logistics company.
You have access to shipment data, SOPs, route/zone maps, and live delivery logs.

Use the retrieved context to answer questions accurately. When analyzing:
- Shipment status & delays: Identify root causes, impacted orders, and severity
- SLA breaches: Highlight which SLAs are at risk or already breached, and by how much
- Driver/route performance: Summarize metrics, flag outliers, suggest improvements

Always be concise, factual, and actionable. If data is insufficient, say so clearly.
Cite specific shipment IDs, driver names, or route codes when available.

Context retrieved:
{context}"""


class LogisticsRAG:
    """Main RAG pipeline for logistics delivery management."""

    def __init__(self, openai_api_key: str, persist_dir: str = "./chroma_db"):
        self.api_key = openai_api_key
        self.persist_dir = persist_dir
        os.environ["OPENAI_API_KEY"] = openai_api_key

        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)
        self.vectorstore = None
        self.chain = None
        self.chat_history: List = []
        self._last_docs: List[Document] = []
        self.loader = LogisticsDocumentLoader()
        self.router = QueryRouter()

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_documents(self, data_dir: str = "./data") -> Dict[str, int]:
        """Load all document types and build / update the vector store."""
        data_path = Path(data_dir)
        all_docs: List[Document] = []
        counts: Dict[str, int] = {}

        shipment_docs = self.loader.load_shipments(data_path / "shipments")
        all_docs.extend(shipment_docs)
        counts["shipments"] = len(shipment_docs)

        sop_docs = self.loader.load_sops(data_path / "sops")
        all_docs.extend(sop_docs)
        counts["sops"] = len(sop_docs)

        route_docs = self.loader.load_routes(data_path / "routes")
        all_docs.extend(route_docs)
        counts["routes"] = len(route_docs)

        log_docs = self.loader.load_logs(data_path / "logs")
        all_docs.extend(log_docs)
        counts["logs"] = len(log_docs)

        if not all_docs:
            print("⚠️  No documents found. Add files to the data/ subdirectories.")
            return counts

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", ",", " ", ""],
        )
        chunks = splitter.split_documents(all_docs)
        counts["total_chunks"] = len(chunks)

        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_dir,
            collection_name="logistics_rag",
        )
        print(f"✅ Ingested {len(chunks)} chunks into vector store.")
        return counts

    def load_existing_vectorstore(self):
        """Load a previously persisted vector store."""
        self.vectorstore = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings,
            collection_name="logistics_rag",
        )
        print("✅ Loaded existing vector store.")

    # ------------------------------------------------------------------
    # Chain setup
    # ------------------------------------------------------------------

    def build_chain(self):
        """Build the conversational retrieval chain using LCEL."""
        if self.vectorstore is None:
            raise RuntimeError("Vector store not initialised. Call ingest_documents() first.")

        retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 8, "fetch_k": 20},
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{question}"),
        ])

        def retrieve_and_store(inputs):
            docs = retriever.invoke(inputs["question"])
            self._last_docs = docs
            return "\n\n".join(doc.page_content for doc in docs)

        self.chain = (
            {
                "context": retrieve_and_store,
                "chat_history": lambda inputs: inputs.get("chat_history", []),
                "question": lambda inputs: inputs["question"],
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        print("✅ RAG chain ready.")

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(self, question: str) -> Dict[str, Any]:
        """Run a question through the RAG pipeline."""
        if self.chain is None:
            raise RuntimeError("Chain not built. Call build_chain() first.")

        intent = self.router.classify(question)

        answer = self.chain.invoke({
            "question": question,
            "chat_history": self.chat_history,
        })

        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))

        sources = []
        for doc in self._last_docs:
            meta = doc.metadata
            sources.append({
                "source": meta.get("source", "unknown"),
                "doc_type": meta.get("doc_type", "unknown"),
                "page": meta.get("page", ""),
                "snippet": doc.page_content[:200],
            })

        return {
            "answer": answer,
            "intent": intent,
            "sources": sources,
        }
