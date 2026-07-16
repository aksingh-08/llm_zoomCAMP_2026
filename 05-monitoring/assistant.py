import sys
import os
from dotenv import load_dotenv
from openai import OpenAI
from ingest import load_faq_data, build_index
from rag_helper import RAGBase

def create_assistant():
    load_dotenv()
    documents = load_faq_data()
    index = build_index(documents)
    return RAGBase(
        index=index,
        llm_client=OpenAI(
            api_key=os.getenv("GITHUB_TOKEN"),
                base_url="https://models.github.ai/inference"
        ),
    )

if __name__ == "__main__":
    assistant = create_assistant()
    query = "How do I join the course?"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    answer = assistant.rag(query)
    print(answer)
    