from openai import OpenAI
from pydantic import BaseModel
import tiktoken

class ClassifiedSnippet(BaseModel):
    snippet: str
    classification: str

def classify_and_process_documents(documents, question, openai_api_key):
    client = OpenAI(api_key=openai_api_key)

    def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def split_text(text, max_tokens=1000):
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            current_chunk.append(word)
            if num_tokens_from_string(" ".join(current_chunk)) > max_tokens:
                chunks.append(" ".join(current_chunk[:-1]))
                current_chunk = [word]

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def classify_snippet(snippet):
        completion = client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "Classify the following text snippet into one of these categories: Grease, Oil Filters, Competitor Oil Filters, or Oils. Only respond with the category name."},
                {"role": "user", "content": f"Text: {snippet}"}
            ]
        )
        return completion.choices[0].message.content.strip()

    processed_docs = []
    for doc in documents:
        snippets = split_text(doc)
        classified_snippets = [
            ClassifiedSnippet(snippet=snippet, classification=classify_snippet(snippet))
            for snippet in snippets
        ]
        processed_docs.extend(classified_snippets)

    completion = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": "You are an expert in automotive products. Answer the following question based on the provided classified document snippets. Provide a comprehensive answer, mentioning the relevant classifications when appropriate."},
            {"role": "user", "content": f"Question: {question}\n\nClassified Snippets:\n{processed_docs}"}
        ]
    )

    return completion.choices[0].message.content.strip()
