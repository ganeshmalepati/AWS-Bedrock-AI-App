"""

   The below code script is for PDF AI Search Assistant. It will search the query inside the PDFs that we have provided and generate the grounded response by using RAG ecosystem.

"""



import os
from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader
)

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS

from langchain_aws import (
    BedrockEmbeddings,
    ChatBedrock
)

from langchain_core.prompts import ChatPromptTemplate

from langchain.chains.combine_documents import (
    create_stuff_documents_chain
)

from langchain.chains import create_retrieval_chain


# ==========================================================
# CONFIGURATION
# ==========================================================

DOCUMENTS_FOLDER = "Docs"
INDEX_PATH = "faiss_index"

AWS_REGION = "us-east-1"

AWS_EMBEDDING_MODEL = "amazon.titan-embed-text-v2:0"

LLM_MODEL = "meta.llama3-70b-instruct-v1:0"


# ==========================================================
# LOAD DOCUMENTS
# ==========================================================

def load_documents(folder_path):

    all_documents = []

    for file_path in Path(folder_path).rglob("*"):

        try:

            # PDF Files
            if file_path.suffix.lower() == ".pdf":

                print(f"Loading PDF: {file_path}")

                loader = PyPDFLoader(str(file_path))

                docs = loader.load()

                for doc in docs:
                    doc.metadata["source"] = str(file_path)
                    doc.metadata["file_name"] = file_path.name
                    doc.metadata["document_type"] = "pdf"

                all_documents.extend(docs)

            # Text Files
            elif file_path.suffix.lower() == ".txt":

                print(f"Loading Text File: {file_path}")

                loader = TextLoader(
                    str(file_path),
                    encoding="utf-8"
                )

                docs = loader.load()

                for doc in docs:
                    doc.metadata["source"] = str(file_path)
                    doc.metadata["file_name"] = file_path.name
                    doc.metadata["document_type"] = "txt"

                all_documents.extend(docs)

        except Exception as e:

            print(f"Error loading file: {file_path}")
            print(e)

    return all_documents


# ==========================================================
# LOAD DOCUMENTS
# ==========================================================

documents = load_documents(DOCUMENTS_FOLDER)

print("\n" + "=" * 80)
print(f"Total Documents Loaded: {len(documents)}")
print("=" * 80)

if len(documents) == 0:
    raise Exception("No documents found in Docs folder")


# ==========================================================
# SPLIT DOCUMENTS
# ==========================================================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=150,
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]
)

chunks = text_splitter.split_documents(documents)

print(f"Total Chunks Created: {len(chunks)}")

if len(chunks) == 0:
    raise Exception("No chunks generated")


# ==========================================================
# BEDROCK EMBEDDINGS
# ==========================================================

embeddings = BedrockEmbeddings(
    model_id=AWS_EMBEDDING_MODEL,
    region_name=AWS_REGION
)

print("\nTesting Embeddings...")

test_embedding = embeddings.embed_query(
    "What is machine learning?"
)

print(
    f"Embedding Vector Length: "
    f"{len(test_embedding)}"
)


# ==========================================================
# FAISS VECTOR STORE
# ==========================================================

if os.path.exists(INDEX_PATH):

    print("\nLoading Existing FAISS Index")

    vector_store = FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

else:

    print("\nCreating New Vector Store")

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    vector_store.save_local(INDEX_PATH)

print("\nVector Store Ready")


# ==========================================================
# RETRIEVER
# ==========================================================

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 3
    }
)




# ==========================================================
# LLM
# ==========================================================

llm = ChatBedrock(
    model_id=LLM_MODEL,
    region_name=AWS_REGION,
    model_kwargs={
        "temperature": 0.1,
        "max_gen_len": 2048
    }
)


# ==========================================================
# PROMPT
# ==========================================================

prompt = ChatPromptTemplate.from_template(
"""
You are a senior technical trainer and interview expert.

Instructions:

1. Use ONLY the supplied context.
2. Do NOT make up information.
3. Combine information from multiple documents when relevant.
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


# ==========================================================
# DOCUMENT CHAIN
# ==========================================================

document_chain = create_stuff_documents_chain(
    llm,
    prompt
)

retrieval_chain = create_retrieval_chain(
    retriever,
    document_chain
)


# ==========================================================
# DEBUG RETRIEVAL
# ==========================================================

def debug_retrieval(query):

    print("\n")
    print("=" * 80)
    print("RETRIEVAL DEBUG")
    print("=" * 80)

    docs = retriever.invoke(query)

    print(f"Retrieved Documents: {len(docs)}")

    for i, doc in enumerate(docs):

        print("\n")
        print("=" * 50)

        print(
            f"Document {i + 1}"
        )

        print(
            f"Source: "
            f"{doc.metadata.get('file_name')}"
        )

        print("-" * 50)

        print(
            doc.page_content[:500]
        )


# ==========================================================
# SIMILARITY SCORE DEBUG
# ==========================================================

def similarity_debug(query):

    print("\n")
    print("=" * 80)
    print("SIMILARITY SEARCH")
    print("=" * 80)

    results = vector_store.similarity_search_with_score(
        query,
        k=5
    )

    for doc, score in results:

        print("\n")
        print("=" * 50)

        print(
            f"Score: {score}"
        )

        print(
            f"Source: "
            f"{doc.metadata.get('file_name')}"
        )

        print(
            doc.page_content[:500]
        )


# ==========================================================
# QUERY LOOP
# ==========================================================

query = "What is Linear regression"

top_docs = retrieve_context(query)

if not top_docs:
    print("No relevant documents found")
    exit()

context = "\n\n".join(
    [
        f"Source: {doc.metadata.get('file_name')}\n{doc.page_content}"
        for doc in top_docs
    ]
)

response = document_chain.invoke(
    {
        "context": top_docs,
        "input": query
    }
)

print("\n")
print("=" * 80)
print("FINAL ANSWER")
print("=" * 80)

print(response)


# _________________________________________________________________________________________________________________________________________________


