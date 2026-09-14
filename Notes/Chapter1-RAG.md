# What RAG Actually Solves

**RAG = Retrieval-Augmented Generation**

The main problem RAG solves is:

> **An AI model may not know your latest, private, or company-specific information. RAG allows the AI to retrieve that information before answering.**

---

# Without RAG

Imagine you ask an AI:

> "What is the leave policy in my company?"

If the AI was never trained on your company's private documents, it doesn't know the answer.

It may guess, which can result in an incorrect answer.

```text
User Question
      ↓
     LLM
      ↓
Answer from model memory
```

---

# With RAG

With RAG, the AI can search your company's documents before answering.

```text
User Question
      ↓
Search / Retrieve
      ↓
Relevant Documents
      ↓
     LLM
      ↓
    Answer
```

For example:

> "How many vacation days do employees get?"

RAG searches the company documents, finds the relevant section, and provides that information to the LLM.

### Key Idea

> **RAG allows an AI to use external documents as a source of information when answering questions.**

---

# Parametric Knowledge vs Retrieved Knowledge

There are two important types of knowledge.

## 1. Parametric Knowledge

Parametric knowledge is information the AI **learned during training**.

Think of it as:

> 🧠 Knowledge stored inside the AI's "brain".

For example:

```text
Paris is the capital of France.
```

This information is stored inside the model's parameters (weights).

### Problems

Parametric knowledge can be:

* Outdated
* Incomplete
* Difficult to verify
* Difficult to update

If new information becomes available, you generally cannot simply edit the model's memory.

---

## 2. Retrieved Knowledge

Retrieved knowledge comes from an **external knowledge source**.

Think of it as:

> 📚 The AI looking something up in a library before answering.

```text
User Question
      ↓
Knowledge Base Search
      ↓
Relevant Documents
      ↓
      LLM
      ↓
    Answer
```

The documents can be updated without retraining the model.

### Advantages

Retrieved knowledge is:

* **Explicit** — You can see the information being used.
* **Updatable** — Documents can be updated without retraining.
* **Auditable** — You can check the source.
* **Useful for private data** — Such as company documents and policies.

---

# RAG vs Long-Context Prompting

Both RAG and long-context prompting allow an AI to work with external information, but they work differently.

## RAG

RAG searches for **only the relevant information**.

Imagine you have:

```text
1,000,000 documents
```

You ask:

> "What is our refund policy?"

RAG might retrieve only a few relevant documents:

```text
Document 342
Document 891
Document 15,203
```

These documents are then provided to the LLM.

### Best For

* Millions of documents
* Large knowledge bases
* Frequently changing information
* Search-based question answering

### Main Limitation

If RAG retrieves the **wrong documents**, the AI may generate a poor answer.

```text
Bad Retrieval
      ↓
Bad Context
      ↓
Bad Answer
```

---

# Long-Context Prompting

Instead of searching for specific documents, you give the AI a large amount of information directly.

```text
Question
   +
Large amount of text
   ↓
  LLM
   ↓
 Answer
```

### Best For

* Small document collections
* A few reports
* A single large document
* Stable information

### Limitations

As the amount of context increases:

* Cost can increase.
* Latency can increase.
* Processing becomes more difficult.
* There is no selective retrieval.

---

# RAG vs Long Context vs Fine-Tuning

| Approach         | Best For                                | Main Limitation                             |
| ---------------- | --------------------------------------- | ------------------------------------------- |
| **RAG**          | Large and changing document collections | Retrieval quality can limit answer quality  |
| **Long Context** | Small, stable document collections      | Cost and latency increase with context size |
| **Fine-Tuning**  | Behavior, style, and task adaptation    | Does not reliably add new factual knowledge |

### Simple Examples

**RAG:**

> "Answer questions using our company documents."

**Long Context:**

> "Here are 50 pages of documents. Summarize them."

**Fine-Tuning:**

> "Make the AI respond in our company's specific style."

---

# Basic RAG Architecture

The basic RAG process looks like this:

```text
                 User Question
                       ↓
                  Retrieval
                       ↓
              Relevant Documents
                       ↓
                 Add to Prompt
                       ↓
                     LLM
                       ↓
                    Answer
```

## Example

### Step 1 — User asks a question

> "What is the company's work-from-home policy?"

### Step 2 — Search

RAG searches the company's knowledge base.

### Step 3 — Retrieve relevant information

It finds:

```text
HR Policy.pdf
Page 12

Work From Home Policy:
Employees can work remotely up to 3 days per week...
```

### Step 4 — Give the information to the LLM

```text
Question:
What is the company's work-from-home policy?

Relevant Information:
Employees can work remotely up to 3 days per week...
```

### Step 5 — Generate the answer

The LLM uses the retrieved information to generate the final response.

---

# When RAG Is the Wrong Solution

RAG is powerful, but it is **not the right solution for every problem**.

## 1. Reasoning Across the Entire Dataset

Suppose you ask:

> "Analyze all 10 million transactions and calculate the overall trend."

Searching for a few documents isn't enough.

A database and data-processing system would be more appropriate.

```text
Database
   ↓
SQL / Data Processing
   ↓
Analysis
```

---

## 2. Structured or Tabular Data

Suppose you have a database:

| Customer | Age | Country | Revenue |
| -------- | --: | ------- | ------: |
| John     |  25 | India   |    5000 |
| Sara     |  31 | USA     |    8000 |

You ask:

> "What is the total revenue from customers in India?"

SQL can calculate this exactly.

```text
Structured Data
      ↓
     SQL
      ↓
Exact Result
```

For structured data and exact calculations:

> **SQL or APIs are usually better than RAG.**

---

## 3. Changing Behavior or Style

Suppose you want the AI to always respond like a professional customer-support agent.

This is a **behavior/style problem**, not a knowledge problem.

You may use:

* Prompt engineering
* System instructions
* Fine-tuning

instead of RAG.

---

## 4. Data Changes Too Quickly

Imagine your source data changes every second:

```text
Actual Data
    ↓
Changes every second

RAG Index
    ↓
Updates every hour
```

The RAG system may retrieve outdated information.

In this situation, you need a faster data-access or indexing strategy.

---

# What RAG Does and Does Not Solve

## RAG Helps With

* Accessing external information
* Using private documents
* Using updated information
* Searching large document collections
* Grounding answers in source documents
* Improving factual recall

## RAG Does Not Automatically Improve

* Reasoning
* Common sense
* Instruction following
* Mathematical reasoning
* Decision-making

### Important Principle

> **RAG improves access to external facts. It does not automatically make the AI better at reasoning.**

For example:

### RAG is useful

> "According to our company handbook, how many sick days are allowed?"

The answer exists in the documents.

### RAG alone may not be enough

> "Given these 20 complicated rules, what is the best business strategy?"

The AI still needs to reason about the information.

---

# Easy Mental Model

Think of an LLM as a person taking an exam.

## Parametric Knowledge

The person answers using what they **remember**.

```text
🧠 Memory
   ↓
Answer
```

## RAG

The person is allowed to **open a textbook and search for relevant information**.

```text
🧠 Memory
   +
📚 Search Documents
   ↓
Answer
```

## Long Context

The person receives the **entire textbook** and is asked to use it.

```text
📚 Entire Textbook
        ↓
       LLM
        ↓
      Answer
```

## Fine-Tuning

The person receives **special training to improve a particular behavior or task**.

```text
Training
   ↓
Better Behavior / Style
```

---

# Key Takeaway

> **RAG = Give the AI a searchable external knowledge base so it can use relevant and up-to-date information instead of relying only on what it learned during training.**
