# from langchain_community.document_loaders import WebBaseLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_aws import ChatBedrock
# from langchain_aws import BedrockEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains.combine_documents import (
#     create_stuff_documents_chain
# )
# from langchain.chains import create_retrieval_chain




# loader = WebBaseLoader("https://docs.smith.langchain.com/tutorials/Administrators/manage_spend")

# docs = loader.load()

# print(f"DOcuments Loaded: {docs}")

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
# text = text_splitter.split_documents(docs)

# print(f"Splitted Text: {text}")
# print(f"Total Chunks: {len(text_chunks)}")

# embeddings = BedrockEmbeddings(
#     model_id="amazon.titan-embed-text-v2:0",
#     region_name="us-east-1"
# )


# vectorstoredb = FAISS.from_documents(text, embeddings)
# print(f"Vector Store Created: {vectorstoredb}")

# query = "LangSmith has two usage limits: total traces and extended"
# result = vectorstoredb.similarity_search(query)
# print(result[0].page_content)


# retriever = vectorstoredb.as_retriever()

# llm = ChatBedrock(
#     model_id="google.gemma-3-12b-it",
#     region_name="us-east-1",
#     model_kwargs={
#         "temperature": 0.5,
#         "max_tokens": 500
#     }
# )

# prompt = ChatPromptTemplate.from_template(
#     """
# Answer the following question based only on the provided context.

# <context>
# {context}
# </context>

# Question:
# {input}
# """
# )

# document_chain = create_stuff_documents_chain(
#     llm,
#     prompt
# )


# retrieval_chain = create_retrieval_chain(
#     retriever,
#     document_chain
# )


# response = retrieval_chain.invoke({
#     "input": "What are the two usage limits in LangSmith?"
# })

# print("\nFINAL ANSWER:\n")
# print(response["answer"])





from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings

from langchain_community.vectorstores import FAISS

from langchain_core.prompts import ChatPromptTemplate

from langchain.chains.combine_documents import (
    create_stuff_documents_chain
)

from langchain.chains import create_retrieval_chain


import os

os.environ["USER_AGENT"] = "Mozilla/5.0"

# ------------------------------------------------
# Load Website
# ------------------------------------------------

loader = WebBaseLoader(
    "https://en.wikipedia.org/wiki/Sai_Pallavi"
)

docs = loader.load()

print(f"Documents Loaded: {len(docs)}")


# ------------------------------------------------
# Split Documents
# ------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=50
)

text = text_splitter.split_documents(docs)

print(f"Total Chunks: {len(text)}")


# ------------------------------------------------
# Embeddings
# ------------------------------------------------

embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    region_name="us-east-1"
)


# ------------------------------------------------
# Vector Store
# ------------------------------------------------

vectorstoredb = FAISS.from_documents(
    text,
    embeddings
)

print("Vector Store Created")


# ------------------------------------------------
# Similarity Search
# ------------------------------------------------

query = "Who is sai pallavi, what she achieved in her life"

result = vectorstoredb.similarity_search(query)

print("\nTop Search Result:\n")
print(result[0].page_content)


# ------------------------------------------------
# Retriever
# ------------------------------------------------

retriever = vectorstoredb.as_retriever()


# ------------------------------------------------
# LLM
# ------------------------------------------------

llm = ChatBedrock(
    model_id="meta.llama3-70b-instruct-v1:0",
    region_name="us-east-1",
    model_kwargs={
        "temperature": 0.5,
        "max_gen_len": 1000,
        "top_p": 0.9
    }
)


# ------------------------------------------------
# Prompt
# ------------------------------------------------

prompt = ChatPromptTemplate.from_template(
    """
Answer the following question based only on the provided context.

<context>
{context}
</context>

Question:
{input}
"""
)


# ------------------------------------------------
# Document Chain
# ------------------------------------------------

document_chain = create_stuff_documents_chain(
    llm,
    prompt
)


# ------------------------------------------------
# Retrieval Chain
# ------------------------------------------------

retrieval_chain = create_retrieval_chain(
    retriever,
    document_chain
)


# ------------------------------------------------
# Invoke
# ------------------------------------------------

response = retrieval_chain.invoke({
    "input": "what are the best films for sai pallavi?"
})

print("\nFINAL ANSWER:\n")

print(response["answer"])