
import streamlit as st

from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings
from langchain_aws import ChatBedrock

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from langchain_core.prompts import ChatPromptTemplate


st.set_page_config(
    page_title="Interview Prep RAG",
    layout="wide"
)

st.title("📚 AI Interview Preparation Assistant")

# -----------------------
# Load Embeddings
# -----------------------

embeddings = BedrockEmbeddings(
    model_id="amazon.titan-embed-text-v2:0",
    region_name="us-east-1"
)

# -----------------------
# Load FAISS
# -----------------------

vector_store = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k":8,
        "fetch_k":30,
        "lambda_mult":0.7
    }
)

# -----------------------
# LLM
# -----------------------

llm = ChatBedrock(
    model_id="meta.llama3-70b-instruct-v1:0",
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

document_chain = create_stuff_documents_chain(
    llm,
    prompt
)

retrieval_chain = create_retrieval_chain(
    retriever,
    document_chain
)

# -----------------------
# Session Memory
# -----------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input(
    "Ask Interview Questions..."
)

if query:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":query
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner("Thinking..."):

        response = retrieval_chain.invoke(
            {
                "input": query
            }
        )

        answer = response["answer"]

        sources = []

        for doc in response["context"]:
            sources.append(
                doc.metadata.get(
                    "file_name",
                    "Unknown"
                )
            )

        final_answer = f"""
{answer}

---
### Sources Used

{', '.join(set(sources))}
"""

    with st.chat_message("assistant"):
        st.markdown(final_answer)

    st.session_state.messages.append(
        {
            "role":"assistant",
            "content":final_answer
        }
    )