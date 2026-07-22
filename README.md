# 🔗 RAGLink

> An enterprise-style AI-powered company knowledge assistant built using Retrieval-Augmented Generation (RAG), hybrid retrieval, reranking, tool-based query routing, and grounded response generation.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Web-Django-green)
![LLM](https://img.shields.io/badge/LLM-Groq%20Llama--3.1-orange)
![RAG](https://img.shields.io/badge/RAG-Hybrid%20Retrieval-purple)
![Vector DB](https://img.shields.io/badge/Vector%20DB-ChromaDB-red)
![Sparse Search](https://img.shields.io/badge/Sparse-BM25-yellow)
![Database](https://img.shields.io/badge/Database-MySQL-blue)
![Embeddings](https://img.shields.io/badge/Embeddings-HuggingFace-green)
![Evaluation](https://img.shields.io/badge/Evaluation-RAGAS-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Project Overview

RAGLink is an enterprise-style AI assistant that allows employees to ask questions about internal company knowledge using natural language.

The system retrieves relevant information from company documents and generates grounded answers using an LLM.

RAGLink supports knowledge retrieval from:

- 🏢 Company Information
- 📋 HR Policies
- 👨‍💼 Employee Handbook
- 💻 Technical Documentation
- 🚀 Project Documentation
- 🔐 Cybersecurity and Compliance
- ☁️ Cloud Infrastructure
- 🧪 QA and DevOps
- 💰 Payroll and Finance

---

## ✨ Features

- 🔍 Semantic Retrieval using ChromaDB
- 🔎 Keyword Retrieval using BM25
- 🔀 Hybrid Retrieval combining semantic and keyword search
- 🎯 Document Reranking for improved relevance
- 🤖 LLM Generation using Groq Llama 3.1
- 🛡️ Grounded Responses to reduce hallucinations
- 🧭 Query Routing for different query types
- 🧮 Calculator Tool for mathematical queries
- 📅 Date Tool for date-related queries
- ⏰ Time Tool for time-related queries
- 🌐 Web Search Tool for external/current information
- 📄 PDF, DOCX and TXT document ingestion
- ✂️ Document Chunking using Recursive Character Text Splitter
- 🗄️ MySQL Database integration
- 🔐 Django Authentication
- 👥 Role-based application structure
- 📚 Retrieved document source tracking
- 🧪 RAGAS evaluation planned for future evaluation and optimization

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       Employee      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Django Web UI    │
                    │       RAGLink       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     ChatService     │
                    │    Query Router     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        Calculator        Date / Time       Web Search
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                        Internal RAG
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Hybrid Retrieval   │
                    │  ChromaDB + BM25    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Reranker       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Context Builder   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Groq Llama 3.1    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Grounded Response  │
                    └─────────────────────┘
````

---

# 📥 Document Ingestion Pipeline

```text
PDF / DOCX / TXT
       │
       ▼
   File Loader
       │
       ▼
Document Cleaning
       │
       ▼
   Text Chunking
       │
       ▼
Embedding Generation
       │
       ├──────────────► chunks.pkl
       │
       ├──────────────► chunk_embeddings.pkl
       │
       └──────────────► ChromaDB
```

Run ingestion:

```bash
python -m rag.ingestion.ingest
```

---

# 🧪 Query Processing Flow

```text
User Question
      │
      ▼
 Query Router
      │
      ├── Calculator ──► Calculate Answer
      │
      ├── Date ────────► Date Answer
      │
      ├── Time ────────► Time Answer
      │
      ├── Web ─────────► Web Search + LLM
      │
      └── RAG
           │
           ▼
     Hybrid Retrieval
           │
           ▼
        Reranking
           │
           ▼
    Context Selection
           │
           ▼
    Prompt Construction
           │
           ▼
     Groq Llama 3.1
           │
           ▼
     Grounded Answer
```

---

# 📁 Project Structure

```text
RAGLink/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
│
├── chatbot/
│   ├── templates/
│   │   └── chatbot/
│   │       └── chat.html
│   ├── services.py
│   ├── views.py
│   └── urls.py
│
├── documents/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── rag/
│   │
│   ├── ingestion/
│   │   ├── ingest.py
│   │   ├── loaders.py
│   │   └── processor.py
│   │
│   ├── chunking/
│   │   └── splitter.py
│   │
│   ├── embeddings/
│   │   └── embedding_model.py
│   │
│   ├── vectorstore/
│   │   └── chroma.py
│   │
│   ├── retrieval/
│   │   ├── retriever.py
│   │   ├── hybrid.py
│   │   └── rerank.py
│   │
│   ├── generation/
│   │   ├── llm.py
│   │   ├── prompt.py
│   │   └── generator.py
│   │
│   ├── tools/
│   │   ├── calculator.py
│   │   ├── date.py
│   │   ├── query_router.py
│   │   └── web_search.py
│   │
│   └── pipeline.py
│
├── media/
│   ├── Company/
│   └── Projects/
│
├── data/
│   ├── chunks.pkl
│   └── chunk_embeddings.pkl
│
├── chroma_db/
│
├── requirements/
│   └── requirements.txt
│
├── templates/
│   └── documents/
│       └── manage_documents.html
│
├── manage.py
├── .env
├── .gitignore
└── README.md
```

---

# 📄 File Responsibilities

| File / Folder                       | Responsibility                                        |
| ----------------------------------- | ----------------------------------------------------- |
| `accounts/`                         | User authentication, roles and account management     |
| `documents/`                        | Document upload, management and database models       |
| `chatbot/`                          | Chat UI, API endpoints and chat service               |
| `config/settings.py`                | Django configuration, MySQL and installed apps        |
| `config/urls.py`                    | Main URL routing                                      |
| `rag/ingestion/ingest.py`           | Main document ingestion pipeline                      |
| `rag/ingestion/loaders.py`          | Loads PDF, DOCX and TXT files                         |
| `rag/ingestion/processor.py`        | Cleans and splits documents into chunks               |
| `rag/chunking/splitter.py`          | Reserved for text splitting logic                     |
| `rag/embeddings/embedding_model.py` | Creates HuggingFace embeddings                        |
| `rag/vectorstore/chroma.py`         | Creates and loads ChromaDB vector store               |
| `rag/retrieval/retriever.py`        | Performs semantic similarity retrieval                |
| `rag/retrieval/hybrid.py`           | Combines semantic and BM25 retrieval                  |
| `rag/retrieval/rerank.py`           | Reranks retrieved documents                           |
| `rag/generation/llm.py`             | Connects RAGLink to Groq Llama 3.1                    |
| `rag/generation/prompt.py`          | Defines grounded-answer prompt rules                  |
| `rag/generation/generator.py`       | Generates answers from retrieved documents            |
| `rag/pipeline.py`                   | Connects retrieval, reranking and generation          |
| `rag/tools/query_router.py`         | Identifies calculator, date, time, web or RAG queries |
| `rag/tools/calculator.py`           | Handles mathematical queries                          |
| `rag/tools/date.py`                 | Handles date and time queries                         |
| `rag/tools/web_search.py`           | Performs external web search                          |
| `media/Company/`                    | Company knowledge documents                           |
| `media/Projects/`                   | Project-related documents                             |
| `data/chunks.pkl`                   | Stores processed document chunks                      |
| `data/chunk_embeddings.pkl`         | Stores generated embeddings                           |
| `chroma_db/`                        | Persistent vector database                            |
| `requirements/requirements.txt`     | Python dependencies                                   |

> **Note:** `rag/chunking/splitter.py` is currently empty. The active chunking logic is currently implemented in `rag/ingestion/processor.py`.

---

# 🛠️ Tech Stack

### Backend

* Python
* Django
* MySQL

### AI / LLM

* Groq
* Llama 3.1
* LangChain
* LangGraph

### RAG

* Retrieval-Augmented Generation
* ChromaDB
* BM25
* Hybrid Retrieval
* Reranking

### Embeddings

* HuggingFace
* Sentence Transformers

### Document Processing

* PyPDF
* PyMuPDF
* python-docx
* Docx2txt

### Evaluation

* RAGAS

### Frontend

* HTML
* CSS
* JavaScript

### Development

* Git
* GitHub
* Python Virtual Environment

---

# 🔄 Current RAG Pipeline

```text
Documents
    │
    ▼
File Loaders
    │
    ▼
Cleaning + Chunking
    │
    ▼
HuggingFace Embeddings
    │
    ▼
ChromaDB + BM25
    │
    ▼
Hybrid Retrieval
    │
    ▼
Reranking
    │
    ▼
Prompt Builder
    │
    ▼
Groq Llama 3.1
    │
    ▼
Grounded Answer + Sources
```

---

# 🚀 Future Improvements

* [ ] Improve multi-hop question handling
* [ ] Add query decomposition
* [ ] Improve retrieval quality
* [ ] Optimize reranking
* [ ] Optimize answer generation
* [ ] Add RAGAS evaluation pipeline
* [ ] Add automated evaluation metrics
* [ ] Improve hallucination detection
* [ ] Add conversation memory
* [ ] Improve source display
* [ ] Expand LangGraph orchestration
* [ ] Add comprehensive unit and integration tests

---

# ▶️ Run Locally

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd RAGLink
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate environment

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements/requirements.txt
```

### 5. Configure environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Ingest documents

```bash
python -m rag.ingestion.ingest
```

### 8. Start Django

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

# 📊 Project Status

### Completed

* ✅ Django application
* ✅ MySQL integration
* ✅ User authentication
* ✅ Document management
* ✅ PDF/DOCX/TXT ingestion
* ✅ Document chunking
* ✅ HuggingFace embeddings
* ✅ ChromaDB vector storage
* ✅ BM25 retrieval
* ✅ Hybrid retrieval
* ✅ Document reranking
* ✅ Groq Llama 3.1 integration
* ✅ Query routing
* ✅ Calculator tool
* ✅ Date and time tools
* ✅ Web search tool
* ✅ Grounded response generation
* ✅ Source tracking

### Planned

* 🔄 RAGAS evaluation
* 🔄 Retrieval optimization
* 🔄 Generation optimization
* 🔄 Query decomposition
* 🔄 Multi-hop retrieval improvements
* 🔄 Improved LangGraph orchestration

---

# 👩‍💻 Author

**Sri Silpa Matukumilli**

B.Tech – Information Technology
Shri Vishnu Engineering College for Women

---

⭐ If you find this project useful, consider giving it a star!

```
```
