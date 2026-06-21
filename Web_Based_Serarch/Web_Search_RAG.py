from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

import os

os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def load_urls(file_path="urls.txt"):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]
    
urls = load_urls()
print(f"Total URLs Loaded: {urls}")

loader = WebBaseLoader(
    urls,
    request_per_second = 3
)
docs = loader.load()
print(f"Documents Loaded: {docs}")


for i, doc in enumerate(docs):
    doc.metadata["source"] = urls[i]


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000, 
    chunk_overlap = 100
)

chunks = text_splitter.split_documents(docs)
print(f"Total Chunks: {chunks}")


embeddings = BedrockEmbeddings(
    model_id = "amazon.titan-embed-text-v2:0",
    region = "us-east-1"
)

INDEX_PATH = "faiss_index"

if os.path.exists(INDEX_PATH):
    print("Loading existing Index")
    vector_store = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
else:
    print("Creating New VectorDB Index")
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(INDEX_PATH)

print("✅ Vector Store Ready")


retriver = vector_store.as_retriver(
    search_type = "mmr",
    search_kargs = {
        "k":5,
        "fetch_k":10
    }
)


def debug_retrieval(query):
    docs = retriever.get_relevant_documents(query)

    print(f"\nRetrieved {len(docs)} docs")

    for i, doc in enumerate(docs):
        print("="*50)
        print(f"Doc {i+1}")
        print(doc.metadata)
        print(doc.page_content[:500])



llm = ChatBedrock(
    model_id= "meta.llama3-70b-instruct-v1:0",
    region_name="us-east-1",
    model_kwargs={
        "temperature":0.5,
        "max_gen_len":2000
    }

)


prompt = ChatPromptTemplate.from_template(
"""
You are a senior technical trainer and interview expert.

Instructions:

1. Use ONLY the supplied context.
2. Do NOT make up information.
3. Combine information from multiple web-links when relevant.
4. Provide a natural explanation instead of listing chunks.
5. Explain concepts clearly as if teaching an interview candidate.

If the answer does not exist in the context, reply exactly:

I don't know based on the provided documents.

Context:
{context}

Question:
{input}

Answer:
"""
)


document_chain = create_stuff_documents_chain(
    llm,
    prompt
)

retrieval_chain = create_retrieval_chain(
    retriever,
    document_chain
)


query = "what are subqueries in mysql, how can we define it, explain it with real time example?"

response = retrieval_chain.invoke(
    {
        "input": query
    }
)

print(response["answer"])
