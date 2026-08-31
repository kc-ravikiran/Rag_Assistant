# 🚚 Logistics Delivery Manager — RAG Assistant

A **Retrieval-Augmented Generation (RAG)** system built with **LangChain + OpenAI** that lets a Delivery Manager ask natural language questions over shipment data, SOPs, route maps, and live delivery logs.

---

## Features

| Capability | Details |
|---|---|
| **Shipment Status & Delays** | Query delayed orders, track by shipment ID, find root causes |
| **SLA Breach Analysis** | Identify breached / at-risk SLAs by zone, route, or carrier |
| **Driver / Route Performance** | Rank drivers by on-time rate, flag underperforming routes |
| **SOP Lookup** | Search escalation procedures, damage handling, return policies |
| **Multi-turn Memory** | Conversation history maintained across questions |
| **Source Citations** | Every answer links back to the source documents |

---

## Project Structure

```
logistics_rag/
├── data/
│   ├── shipments/     ← CSV / Excel shipment & order files
│   ├── sops/          ← SOP PDF documents (or .txt)
│   ├── routes/        ← Route/zone CSVs or JSON
│   └── logs/          ← Live delivery log CSVs or .log files
├── src/
│   ├── rag_engine.py          # Core RAG pipeline
│   ├── document_loaders.py    # Loaders for all data types
│   ├── query_router.py        # Intent classifier
│   └── txt_loader.py          # .txt SOP fallback loader
├── generate_sample_data.py    # Creates test data
├── ingest.py                  # Build / refresh vector store
├── chat.py                    # Interactive CLI chat
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

```bash
export OPENAI_API_KEY="sk-..."
# or create a .env file:
echo "OPENAI_API_KEY=sk-..." > .env
```

### 3. Add your data

Place your files in the appropriate `data/` subdirectories:

| Folder | Accepted formats | Contains |
|---|---|---|
| `data/shipments/` | `.csv`, `.xlsx` | Order/shipment records |
| `data/sops/` | `.pdf`, `.txt` | Standard Operating Procedures |
| `data/routes/` | `.csv`, `.json` | Route codes, zones, hubs |
| `data/logs/` | `.csv`, `.log` | Live delivery events |

**No real data yet?** Generate sample data:

```bash
python generate_sample_data.py
```

### 4. Ingest documents (build vector store)

```bash
python ingest.py
```

This chunks all documents and stores embeddings in `./chroma_db/`.  
**Re-run whenever your data changes.**

### 5. Start chatting

```bash
python chat.py
```

---

## Expected CSV Schemas

### `data/shipments/*.csv`

| Column | Description |
|---|---|
| `shipment_id` | Unique ID (e.g. SHP00001) |
| `order_id` | Customer order ID |
| `customer_name` | Customer name |
| `origin` / `destination` | City names |
| `carrier` | Carrier name |
| `driver_id` / `driver_name` | Assigned driver |
| `status` | Delivered / In Transit / Delayed / etc. |
| `zone` | Delivery zone |
| `route_code` | Route code |
| `scheduled_delivery` | ISO datetime |
| `actual_delivery` | ISO datetime (blank if not yet) |
| `delay_minutes` | Minutes past scheduled time |
| `sla_status` | Met / At Risk / Breached |

### `data/logs/*.csv`

| Column | Description |
|---|---|
| `timestamp` | Event time |
| `shipment_id` | Related shipment |
| `event` | Picked Up / Delivered / Failed / etc. |
| `driver_id` / `driver_name` | Driver |
| `location` | Current city |
| `notes` | Optional notes |

---

## Sample Questions

```
"Which shipments are delayed by more than 60 minutes?"
"Show me all SLA breaches in the North zone today."
"Which driver has the highest on-time rate?"
"What is the SOP for handling a failed delivery?"
"List shipments with status 'Returned'."
"Which route has the most delays?"
"How should I escalate a Level 3 delay?"
```

---

## Architecture

```
User Query
    │
    ▼
Query Router ──► Intent: shipment_status / sla_breach / driver_performance
    │
    ▼
Retriever (ChromaDB MMR, top-8 chunks)
    │
    ▼
ConversationalRetrievalChain
    │                   │
    ▼                   ▼
GPT-4o LLM    ConversationBufferMemory
    │
    ▼
Answer + Source Documents
```

---

## Configuration

Edit `src/rag_engine.py` to adjust:

- `model="gpt-4o"` — swap to `gpt-4o-mini` to reduce costs
- `search_kwargs={"k": 8}` — number of retrieved chunks
- `chunk_size=1000` — chunk size for text splitting
- `SYSTEM_PROMPT` — customise the assistant's persona/instructions
