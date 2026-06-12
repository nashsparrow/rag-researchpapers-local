


from app.document_retrieval.document_retrieval import load_model


def create_context(chunks : any):
    context = ""
    sources = []

    for chunk in chunks:
        chunk_sources = {}
        chunk_context = f'[{chunk.get("filename", "")} | Page: {chunk.get("page_number", "")} | Chunk Index: {chunk.get("chunk_index", "")}] {chunk.get("text", "")}'
        context += chunk_context + "\n"
        chunk_sources["filename"] = chunk.get("filename", "")
        chunk_sources["page_number"] = chunk.get("page_number", "")
        sources.append(chunk_sources)

    return {"context": context, "sources": sources}