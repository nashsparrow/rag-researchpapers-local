import os
import uuid

from app.context_creator.context_creator import create_context
from app.document_chunking.chunking import chunk_document
from app.document_embedding.embedding import create_embeddings, get_index, save_index
from app.document_ingestion.document_loader import load_pdf_to_document
from app.document_retrieval.document_retrieval import (
    load_model,
    retrieve_relevant_chunks,
)
from app.helpers.data_classes import FlattenedChunkedJSONFileData
from app.helpers.helpers import extract_sources, save_json
from app.helpers.text_cleanup import clean_text
from app.llm_integration.llm_integration import send_query_to_llm
from app.testing_accuracy.rag_testing import (
    test_answer_accuracy,
    test_recall_accuracy,
    test_retrieval_accuracy,
)
from config import CHUNK_SIZE


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

                # Clean text
                cleaned_text = clean_text(text)

                # Chunk the document
                chunked_data = chunk_document(
                    cleaned_text, chunk_size=CHUNK_SIZE
                )  # Example chunk size
                for i, chunk in enumerate(chunked_data):
                    flattened_chunk = FlattenedChunkedJSONFileData(
                        file_id=file_id,
                        filename=filename,
                        chunk_id=str(uuid.uuid4()),
                        chunk_index=i,
                        page_number=page.number + 1,
                        text=chunk,
                        char_count=len(chunk),
                    )
                    json_array.append(flattened_chunk)
                    # Embeddings for each chunk

                    embeddings = create_embeddings(chunk)
                    index.add(embeddings)

            print(f"Finished processing file: {filename}")

    save_json([chunk.to_dict() for chunk in json_array], txt_path + "chunked_data.json")
    save_index(index, os.path.join(txt_path, "document_embeddings.index"))


def execute_query_pipeline(top_k=3):
    model, index, chunks = load_model()

    while True:
        question = input("Enter your question (or 'exit' to quit): ")

        if question.lower() == "exit":
            break

        relevant_chunks = retrieve_relevant_chunks(
            question, model, index, chunks, top_k
        )

        context_and_sources = create_context(relevant_chunks)
        # print("Context:\n", context_and_sources["context"])
        # print("Sources:\n", context_and_sources["sources"])

        response = send_query_to_llm(question, context_and_sources["context"])
        #print(response)

        print("LLM Response:\n", response.message.content)
        # print(extract_sources(context_and_sources["sources"]))
        print("\n")

def exeute_recall_at_tests():
    # should run after the indexing pipeline is executed.
    print("Starting Recall@ Tests..")
    model, index, chunks = load_model()

    chunk_sizes = [1, 3, 5, 7]
    
    for i in chunk_sizes:
        print(f"Running Recall@ {i} Tests..")
        test_recall_accuracy(model, index, chunks, top_k=i)
        print(f"Recall@ {i} Test Completed")

    print(f"Recall@ Tests Completed")

def execute_test_pipeline():
    # should run after the indexing pipeline is executed.
    model, index, chunks = load_model()

    print("Running Retrieval Tests..")
    test_retrieval_accuracy(model, index, chunks)
    print("Retrieval Tests completed.")

    print("Running Answer Accuray Tests..")
    test_answer_accuracy(model, index, chunks)
    print("Answer Accuray Tests completed.")
