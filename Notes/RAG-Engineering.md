# RAG Engineering



## Document ingestion
Document ingestion simply means taking a document and putting its information into a system so the system can understand and use it.
For example:

**PDF** → Upload → Extract text → Process information → Store → Search/Analyze

If you upload a **PDF** to an AI system, document ingestion might:

Read the **PDF**. Extract the text, tables, and images. Break the content into smaller pieces. Convert the information into a format the AI can understand. Store it so you can later search, ask questions, or analyze the document.

In simple words:

📄 Document ingestion = Getting information from documents into a system in a usable form.

## Challenges in document ingestion
The main challenges in document ingestion are:

**Different file formats** — PDFs, Word files, Excel sheets, scanned documents, etc. all need different handling.
**Poor document quality** — Scanned or blurry documents can make text extraction inaccurate. 
**Complex layouts** — Tables, columns, headers, footnotes, and images can be difficult to interpret correctly. 
**OCR** errors — Handwritten or scanned text may be incorrectly recognized.
**Large documents** — Very long documents need to be split into smaller sections before processing.
**Maintaining context** — When a document is split, the system may lose the connection between related information. 
**Data privacy & security** — Documents may contain sensitive or confidential information. 
**Duplicate documents** — The same document may be uploaded multiple times, creating redundant data. 
**Accuracy** — Extracted information needs to be validated because small errors can affect the final results. 
**Searchability** — The ingested content needs to be organized properly so users or AI systems can find the right information quickly.

In short:

The biggest challenge is turning messy, differently formatted documents into clean, accurate, searchable information without losing meaning or context.


# Document Sources & Loaders

Different types of documents have different structures and challenges.
**Document loaders** extract useful information from these sources and convert it into a format that AI systems can process.

## 1. PDF

### Challenges

* Multiple columns
* Headers and footers
* Tables
* Scanned pages
* Complex layouts

### Techniques

* **PDFMiner** – Extracts text from PDFs.
* **pdfplumber** – Extracts text, tables, and layout information.
* **OCR** – Used when the PDF contains scanned images instead of actual text.

### Example

```text
PDF
 ↓
Extract text
 ↓
Clean and process
 ↓
AI / Search
```

---

## 2. HTML / Web Pages

### Challenges

Web pages contain a lot of unnecessary content:

* Navigation menus
* Advertisements
* Headers
* Footers
* Comments
* Other boilerplate content

### Techniques

* **Readability extraction** – Identifies and extracts the main content.
* **DOM pruning** – Removes unnecessary HTML elements.

### Example

```text
Web Page
 ├── Navigation      → Remove
 ├── Advertisement   → Remove
 ├── Header          → Remove
 ├── Main Article    → Keep
 └── Footer          → Remove
```

---

## 3. Markdown

Markdown documents have a useful structure based on headings.

### Challenges

* Fenced code blocks
* Links
* Images
* Headings
* Maintaining document structure

### Technique

Use **structure-aware splitting** based on headings.

### Example

```markdown
# Machine Learning

## Supervised Learning

Supervised learning uses labeled data.

## Unsupervised Learning

Unsupervised learning finds patterns in data.
```

Instead of splitting the document randomly, we can split it according to its headings.

```text
# Machine Learning
        ↓
## Supervised Learning
        ↓
## Unsupervised Learning
```

---

## 4. Tables

Tables can be difficult for AI systems to understand because they may contain:

* Multi-row headers
* Merged cells
* Complex layouts
* Relationships between rows and columns

### Example

| Product |  2025 |  2026 |
| ------- | ----: | ----: |
|         | Sales | Sales |
| Laptop  |   100 |   150 |

The system needs to understand that:

```text
Laptop
 ├── 2025 Sales: 100
 └── 2026 Sales: 150
```

### Techniques

Tables can be **linearized** into readable text:

```text
Product: Laptop
2025 Sales: 100
2026 Sales: 150
```

Or converted into structured formats such as **CSV** or **JSON**.

### JSON Example

```json
{
  "product": "Laptop",
  "2025_sales": 100,
  "2026_sales": 150
}
```

---

## 5. Structured Data

Structured data includes:

* JSON
* XML
* Database records
* API responses

### Challenges

* Schema drift
* Nested objects
* Missing or `null` values
* Changing data structures

### Example

```json
{
  "user": {
    "name": "John",
    "age": 25
  }
}
```

### Techniques

Convert structured data into meaningful text:

```text
User name: John
User age: 25
```

The **schema can also be provided as context** so the AI understands what each field represents.

### Simple Flow

```text
Structured Data
       ↓
Serialize
       ↓
Meaningful Text
       ↓
AI Processing
```

---

## 6. Scanned Documents

A scanned document is usually an image rather than actual machine-readable text.

### Challenge

Normal text extraction may return nothing:

```text
Scanned Document
       ↓
Text Extraction
       ↓
❌ No Text
```

### Technique

Use **OCR (Optical Character Recognition)** to recognize text from the image.

Common approaches include:

* **Tesseract OCR**
* **Layout-aware models** for documents containing complex layouts, tables, and images

### Example

```text
Scanned Document
       ↓
      OCR
       ↓
Extracted Text
       ↓
Clean & Process
       ↓
AI / Search
```

---

# Summary

| Source                | Main Challenges                           | Key Techniques                      |
| --------------------- | ----------------------------------------- | ----------------------------------- |
| **PDF**               | Columns, headers, footers, scanned images | PDFMiner, pdfplumber, OCR           |
| **HTML / Web**        | Boilerplate, navigation, advertisements   | Readability extraction, DOM pruning |
| **Markdown**          | Code blocks, links, images, structure     | Heading-based splitting             |
| **Tables**            | Multi-row headers, merged cells           | Linearization, CSV, JSON            |
| **Structured Data**   | Schema drift, nested objects, null values | Serialization, schema context       |
| **Scanned Documents** | No extractable text                       | Tesseract OCR, layout-aware models  |

## Key Takeaway

> **Document ingestion is the process of taking different types of raw documents, extracting useful information, cleaning it, and converting it into a format that AI systems can understand and process.**
