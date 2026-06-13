# Compiler RAG Assistant

This is a Retrieval Augmented Generation (RAG) system that helps you ask questions about compiler optimization research papers and LLVM documentation. Instead of reading through PDFs manually, you can ask a question and the system will find the relevant parts of your documents and generate an answer using an AI model.

## How It Works

The project is organized into several modules that work together:

```
rag-researchpapers-azure/
├── app/
│   ├── document_ingestion/          # Loads PDFs from disk
│   │   └── document_loader.py
│   ├── helpers/                     # Utility functions
│   │   ├── data_classes.py          # Data structures
│   │   ├── helpers.py               # File operations
│   │   └── text_cleanup.py          # Text normalization
│   ├── document_chunking/           # Breaks text into pieces
│   │   └── chunking.py
│   ├── document_embedding/          # Converts text to vectors
│   │   └── embedding.py
│   ├── document_retrieval/          # Finds relevant chunks
│   │   └── document_retrieval.py
│   ├── context_creator/             # Formats chunks for the LLM
│   │   └── context_creator.py
│   ├── llm_integration/             # Talks to the AI model
│   │   └── llm_integration.py
│   └── pipeline.py                  # Main orchestration
├── data/
│   ├── pdf/                         # Put your PDFs here
│   └── processed/                   # Generated indexes and embeddings
├── config.py                        # Settings
└── README.md
```

## What Happens When You Index Your Documents

Here's the step-by-step process:

1. **Load PDFs** — The system reads all PDF files from your `data/pdf/` folder

2. **Clean Text** — It removes headers, footers, and formatting noise to get clean, readable text

3. **Split into Chunks** — Long documents are broken into manageable pieces (around 500 characters each) so the AI can process them

4. **Create Embeddings** — Each chunk is converted into a mathematical representation (vector) that captures its meaning. We use the BAAI/bge-small-en-v1.5 model for this

5. **Build Search Index** — All these vectors are organized into a FAISS index, which lets us quickly find similar chunks

6. **Save Everything** — The embeddings and chunk metadata are saved to `data/processed/` for future queries

## How Querying Works

When you ask a question:

1. Your question gets converted to an embedding (same way as the chunks)
2. The system searches the FAISS index to find the top 3 most similar chunks
3. These chunks are scored by relevance
4. The chunks are formatted with source information (filename, page number)
5. Everything is sent to Ollama (llama3.2) along with a system prompt
6. The LLM reads the context and generates an answer
7. You get a concise response with source attribution

## Setup

First, update `config.py` if you want to change defaults:

```python
MODEL_NAME = "BAAI/bge-small-en-v1.5"      # Which embedding model to use
NORMALIZE_EMBEDDINGS = True                 # Keep this on for better results
PROCESSED_DATA_PATH = "data/processed/"     # Where to save indexes
PDF_DATA_PATH = "data/pdf/"                 # Where your PDFs go
CHUNK_SIZE = 500                            # How big each chunk is (characters)
```

## Getting Started

### Step 1: Add Your Documents
Place your PDF files in the `data/pdf/` folder.

### Step 2: Build the Index
To process your PDFs and build the search index:

```bash
python3 -m app.pipelines
```

Make sure the `execute_indexing_pipeline()` call is uncommented in `pipeline.py`. This will:
- Read all your PDFs
- Clean and chunk the text
- Create embeddings
- Build the search index
- Save everything for later use

This can take a while depending on how many PDFs you have.

### Step 3: Start Asking Questions
Once indexing is done, you can query the system:

```bash
python3 -m app.pipelines
```

The `execute_query_pipeline()` function will start an interactive loop where you can ask questions. Type your question and press Enter. Type 'exit' when you're done.

### Testing
Run the indexing pipeline first, then call `test_retrieval_accuracy()` and/or `test_answer_accuracy()` from `execute_test_pipeline()` in `app/pipelines.py`.

```bash
python3 -m app.pipelines
```

Retrieval tests use `data/test_files/retrieval_evaluation_questions.json`. Answer tests use `data/test_files/answer_evaluation.json` and require Ollama with `llama3.2`. Results are saved as timestamped reports in `data/test_files/`:

- `retrieval_accuracy_<timestamp>.txt`
- `answer_accuracy_<timestamp>.txt`

## What's Happening Behind the Scenes

**Embedding Model**: We use a lightweight but effective model (BAAI/bge-small-en-v1.5) that's specifically tuned for retrieval tasks. It's fast and doesn't need a GPU.

**Vector Search**: FAISS uses inner product search with L2-normalized embeddings to find the most relevant chunks. It's super fast even with thousands of chunks.

**Local AI**: The system uses Ollama with llama3.2 running locally on your machine. No data is sent to external APIs—everything stays on your computer.

## Recent Improvements

- **Fixed embedding issues** — Ensured embeddings always have the right shape for FAISS
- **Lazy loading** — Models are only loaded when needed, not on startup
- **Better message format** — Fixed how questions and context are sent to the LLM
- **Relevance scores** — Retrieved chunks now include their similarity scores
- **Proper response parsing** — We extract just the answer from the LLM's response
- **Context integration** — Context and questions are properly formatted for the LLM

## You'll Need These

- **pymupdf** — For reading PDFs
- **sentence-transformers** — For creating embeddings
- **faiss-cpu** — For fast similarity search
- **ollama** — For running the LLM locally
- **ftfy** — For fixing text encoding issues
- Plus a few others for utilities and data handling

## Ideas for the Future

- Support more document formats (Word, HTML, etc.)
- Train the embeddings model specifically on compiler papers
- Filter results by date, author, or keywords
- Build a web interface so you don't need the command line
- Remember conversation history across multiple questions
- Show exactly where in the PDF each answer came from 
