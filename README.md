# Compiler RAG Assistant

RAG-based assistant for compiler optimization papers and LLVM documentation using embeddings, vector search, and LLMs.


## Steps

1. Document loading with pymupdf. Loading all pdfs in the data/pdf folder
2. Document validation with manual functions 
3. Text clean up with ftfy and manual functions for normalize_whitespace, fix_broken_lines, remove_empty_blocks, remove_headers_footers, format_metadata
4. Chunking with spacy. (chunk sentences for 1000 size chunks. Overlap 1 sentence)
5. Embedding the chunks with sentence-transformers using "BAAI/bge-small-en-v1.5" model
6. Retrieval pipeline implemented. 
