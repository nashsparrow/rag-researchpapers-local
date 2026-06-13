import json
import re
from datetime import datetime

from app.context_creator.context_creator import create_context
from app.document_retrieval.document_retrieval import retrieve_relevant_chunks
from app.llm_integration.llm_integration import send_query_to_llm
from config import RECALL_TEST_DATA_PATH, TEST_DATA_PATH


def test_retrieval_accuracy(model, index, chunks):
    with open(f"{TEST_DATA_PATH}retrieval_evaluation_questions.json", "r") as f:
        test_file = json.load(f)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_path = f"{TEST_DATA_PATH}test_results_retrieval_accuracy_{timestamp}.txt"
    report_lines = []
    total_questions = len(test_file.get("questions", []))
    overall_top_1_hits = 0
    overall_top_3_hits = 0
    overall_top_5_hits = 0
    overall_keyword_hits = 0

    for test in test_file["questions"]:
        question = test["question"]
        expected_sources = test.get("expected_sources", [])
        expected_keywords = test.get("expected_keywords", [])

        relevant_chunks = retrieve_relevant_chunks(
            question, model, index, chunks, top_k=3
        )

        def chunk_matches_expected_source(chunk, expected_source):
            return chunk.get("filename") == expected_source.get(
                "filename"
            ) and chunk.get("page_number") in expected_source.get("pages", [])

        def matches_any_expected_source(chunk):
            return any(
                chunk_matches_expected_source(chunk, source)
                for source in expected_sources
            )

        top_1_hit = False
        top_3_hit = False
        top_5_hit = False
        keyword_hit = False

        retrieved_source_hits = []
        retrieved_text = " ".join(
            chunk.get("text", "")
            for chunk in relevant_chunks
            if isinstance(chunk, dict)
        )
        retrieved_text_lower = retrieved_text.lower()

        for idx, chunk in enumerate(relevant_chunks, start=1):
            if not isinstance(chunk, dict):
                continue

            matches_source = matches_any_expected_source(chunk)
            if idx == 1 and matches_source:
                top_1_hit = True
            if idx <= 3 and matches_source:
                top_3_hit = True
            if idx <= 5 and matches_source:
                top_5_hit = True

            retrieved_source_hits.append(
                (chunk.get("filename"), chunk.get("page_number"), matches_source)
            )

        for keyword in expected_keywords:
            if keyword.lower() in retrieved_text_lower:
                keyword_hit = True
                break

        overall_top_1_hits += 1 if top_1_hit else 0
        overall_top_3_hits += 1 if top_3_hit else 0
        overall_top_5_hits += 1 if top_5_hit else 0
        overall_keyword_hits += 1 if keyword_hit else 0

        report_lines.append(f"Question: {question}")
        report_lines.append(f"Expected Sources: {expected_sources}")
        report_lines.append(f"Retrieved Chunks: {retrieved_source_hits}")
        report_lines.append(
            f"top_1_hit: {top_1_hit}, top_3_hit: {top_3_hit}, "
            f"top_5_hit: {top_5_hit}, keyword_hit: {keyword_hit}"
        )
        report_lines.append(f"Expected Keywords: {expected_keywords}\n")

    if total_questions > 0:
        report_lines.append("=== Overall Retrieval Accuracy ===")
        report_lines.append(f"Questions evaluated: {total_questions}")
        report_lines.append(
            f"top_1 accuracy: {overall_top_1_hits / total_questions:.2f}"
        )
        report_lines.append(
            f"top_3 accuracy: {overall_top_3_hits / total_questions:.2f}"
        )
        report_lines.append(
            f"top_5 accuracy: {overall_top_5_hits / total_questions:.2f}"
        )
        report_lines.append(
            f"keyword accuracy: {overall_keyword_hits / total_questions:.2f}"
        )

    with open(output_path, "w") as output_file:
        output_file.write("\n".join(report_lines))


def test_answer_accuracy(model, index, chunks):
    with open(f"{TEST_DATA_PATH}answer_evaluation.json", "r") as f:
        test_file = json.load(f)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_path = f"{TEST_DATA_PATH}test_results_answer_accuracy_{timestamp}.txt"
    report_lines = []
    total_questions = len(test_file.get("questions", []))
    overall_correct_answers = 0
    overall_grounded_answers = 0
    overall_correct_citations = 0
    overall_hallucinations = 0

    def source_matches_expected(source, expected_source):
        return source.get("filename") == expected_source.get("filename") and source.get(
            "page_number"
        ) in expected_source.get("pages", [])

    def response_content(response):
        message = getattr(response, "message", None)
        if message is not None:
            content = getattr(message, "content", None)
            if content is not None:
                return content

        if isinstance(response, dict):
            message = response.get("message", {})
            if isinstance(message, dict):
                return message.get("content", "")

        return ""

    def cites_expected_source(answer, expected_sources):
        answer_lower = answer.lower()
        for source in expected_sources:
            filename = str(source.get("filename", "")).lower()
            if not filename or filename not in answer_lower:
                continue

            for page in source.get("pages", []):
                page_pattern = rf"\bpage\s*:?\s*{re.escape(str(page))}\b"
                if re.search(page_pattern, answer_lower):
                    return True
        return False

    for test in test_file.get("questions", []):
        question = test["question"]
        reference_answer = test.get("reference_answer", "")
        expected_sources = test.get("expected_sources", [])
        required_keywords = test.get("must_include_keywords", [])

        relevant_chunks = retrieve_relevant_chunks(
            question, model, index, chunks, top_k=5
        )
        context_and_sources = create_context(relevant_chunks)
        response = send_query_to_llm(question, context_and_sources["context"])
        answer = response_content(response)

        answer_lower = answer.lower()
        context_lower = context_and_sources["context"].lower()
        matched_keywords = [
            keyword for keyword in required_keywords if keyword.lower() in answer_lower
        ]
        unsupported_keywords = [
            keyword
            for keyword in matched_keywords
            if keyword.lower() not in context_lower
        ]

        answer_correct = bool(required_keywords) and len(matched_keywords) == len(
            required_keywords
        )
        expected_source_retrieved = any(
            source_matches_expected(source, expected_source)
            for source in context_and_sources["sources"]
            for expected_source in expected_sources
        )
        grounded = (
            answer_correct and expected_source_retrieved and not unsupported_keywords
        )
        citation_correct = cites_expected_source(answer, expected_sources)
        hallucination = bool(unsupported_keywords)

        overall_correct_answers += 1 if answer_correct else 0
        overall_grounded_answers += 1 if grounded else 0
        overall_correct_citations += 1 if citation_correct else 0
        overall_hallucinations += 1 if hallucination else 0

        report_lines.append(f"Question: {question}")
        report_lines.append(f"Reference Answer: {reference_answer}")
        report_lines.append(f"Generated Answer: {answer}")
        report_lines.append(f"Required Keywords: {required_keywords}")
        report_lines.append(f"Matched Keywords: {matched_keywords}")
        report_lines.append(
            f"answer_correct: {answer_correct}, grounded: {grounded}, "
            f"citation_correct: {citation_correct}, hallucination: "
            f"{'yes' if hallucination else 'no'}\n"
        )

    if total_questions > 0:
        report_lines.append("=== Overall Answer Accuracy ===")
        report_lines.append(f"Questions evaluated: {total_questions}")
        report_lines.append(
            f"answer accuracy: {overall_correct_answers / total_questions:.2f}"
        )
        report_lines.append(
            f"grounded accuracy: {overall_grounded_answers / total_questions:.2f}"
        )
        report_lines.append(
            f"citation accuracy: {overall_correct_citations / total_questions:.2f}"
        )
        report_lines.append(
            f"hallucination rate: {overall_hallucinations / total_questions:.2f}"
        )

    with open(output_path, "w") as output_file:
        output_file.write("\n".join(report_lines))

def test_recall_accuracy(model, index, chunks, top_k):
    with open(f"{RECALL_TEST_DATA_PATH}recall_evaluation.json", "r") as f:
        test_file = json.load(f)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_path = f"{RECALL_TEST_DATA_PATH}recall_test_result_size_{top_k}_{timestamp}.txt"
    report_lines = []
    total_items = len(test_file.get("data", []))
    correct_items = 0

    for test in test_file["data"]:
        question = test["question"]
        expected_chunk_id = test.get("expected_chunk_id")

        relevant_chunks = retrieve_relevant_chunks(
            question, model, index, chunks, top_k
        )

        for relevant_chunk in relevant_chunks:
            if (expected_chunk_id == relevant_chunk["chunk_id"]):
                correct_items += 1

    report_lines.append(f"Recall@: {top_k}")
    report_lines.append(f"correct items: {correct_items}")
    report_lines.append(f"total items: {total_items}")
    report_lines.append(f"Accuracy: {correct_items / total_items}")

    with open(output_path, "w") as output_file:
        output_file.write("\n".join(report_lines))


