from spacy.lang.en import English


def chunk_document(document: str, chunk_size: int) -> list:
    nlp = English()
    nlp.add_pipe("sentencizer")
    doc = nlp(document)

    sentences = [sent.text.strip() for sent in doc.sents]
    chunks = []
    current_chunk = sentences[0] if sentences else ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            current_chunk += sentence
            chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
