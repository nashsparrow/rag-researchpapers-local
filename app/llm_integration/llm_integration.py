from ollama import chat


def build_system_prompt():
    prompt = "You are a technical research assistant.\n\n"
    prompt += "If the context contains relevant information, answer using it.\n\n"
    prompt += (
        "If the context does not contain relevant information, say you don't know.\n\n"
    )
    prompt += "Keep the answer concise.\n\n"
    prompt += "For every statement ONLY If the answer is found, cite the file name and the page numbers used at the end of the answer in the format [filename: name , page: 2]."
    return prompt


def send_query_to_llm(question, context):
    # Used Ollama with llama3.2
    response = chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )

    return response
