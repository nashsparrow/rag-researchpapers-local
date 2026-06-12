import os
import uuid

from app.context_creator.context_creator import create_context
from app.document_chunking.chunking import chunk_document
from app.document_embedding.embedding import create_embeddings, get_index, save_index
from app.document_ingestion.document_loader import load_pdf_to_document
from app.document_retrieval.document_retrieval import load_model, retrieve_relevant_chunks
from app.helpers.data_classes import FlattenedChunkedJSONFileData
from app.helpers.data_classes import FlattenedChunkedJSONFileData
from app.helpers.helpers import save_json
from app.helpers.text_cleanup import clean_text
from app.llm_integration.llm_integration import send_query_to_llm
from config import CHUNK_SIZE, PDF_DATA_PATH, PROCESSED_DATA_PATH



def execute_indexing_pipeline(pdf_path: str, txt_path: str):

    print("Starting the document processing pipeline...")
    json_array = []
    index = get_index()
    # Validate and Load the document
    for filename in os.listdir(pdf_path):
            if filename.endswith(".pdf"):

                print(f"Processing file: {filename}")
                doc = load_pdf_to_document(os.path.join(pdf_path, filename))
                file_id = str(uuid.uuid4())
                for page in doc:
                    text = page.get_text()

                    #Clean text
                    cleaned_text = clean_text(text)

                    #Chunk the document
                    chunked_data = chunk_document(cleaned_text, chunk_size=CHUNK_SIZE)  # Example chunk size
                    for i, chunk in enumerate(chunked_data):
                        flattened_chunk = FlattenedChunkedJSONFileData(
                            file_id=file_id,
                            filename=filename,
                            chunk_id=str(uuid.uuid4()),
                            chunk_index=i,
                            page_number=page.number + 1,
                            text=chunk,
                            char_count=len(chunk)
                        )
                        json_array.append(flattened_chunk)
                        #Embeddings for each chunk

                        embeddings = create_embeddings(chunk)
                        index.add(embeddings)

                print(f"Finished processing file: {filename}")


    save_json([chunk.to_dict() for chunk in json_array], txt_path + "chunked_data.json")         
    save_index(index, os.path.join(txt_path, "document_embeddings.index"))


def execute_query_pipeline(top_k=3):
    model, index, chunks = load_model()

    while True:
        question = input("Enter your question (or 'exit' to quit): ")

        if question.lower() == 'exit':
            break

        relevant_chunks = retrieve_relevant_chunks(question, model, index, chunks, top_k)
        
        context_and_sources = create_context(relevant_chunks)
        # print("Context:\n", context_and_sources["context"])
        # print("Sources:\n", context_and_sources["sources"])

        response = send_query_to_llm(question, context_and_sources["context"])

        print("LLM Response:\n", response.message.content) 

## when indexing pipeline is executed.
# ##execute_indexing_pipeline(pdf_path=PDF_DATA_PATH, txt_path=PROCESSED_DATA_PATH)

## to query the indexed data
print (execute_query_pipeline())