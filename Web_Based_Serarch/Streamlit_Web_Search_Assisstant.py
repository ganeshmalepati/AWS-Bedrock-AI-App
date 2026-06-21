import streamlist as st
import os 

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain




# CONFIG
# ---------------------------------------------
os.environ["USER_AGENT"] = "Mozilla/5.0"
INDEX_PATH = "faiss_index"


def load_urls(file_path="urls.txt"):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]
    

@st.cache.resource
def get_vectorstore():
    urls = load_urls()

    embeddings = BedrockEmbeddings(
        model_id="amazon.titan-embed-text-v2:0",
        region_name="us-east-1"
    )

    if os.path.exists(INDEX_PATH):
        vectorstore = FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vectorstore
    
    loader = WebBaseLoader(urls, requests_per_second=3)
    docs = loader.load()

    for i, doc in enumerate(docs):
        doc.metadata["source"]=urls[i]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000
        chunk_overlap = 100
    )

    documents = splitter.split_documents(docs)

    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(INDEX_PATH)

    return vectorstore

def llm():
    return ChatBedrock(
        model_id = "meta.llama3-70b-instruct-v1:0",
        region_name = "us-east-1",
        streaming = True
        model_kwargs = {
            "temperature":0.5,
            "max_gen_len":1000
        }
    )

prompt = ChatPromptTemplate.from_template(
"""
You are a senior technical trainer, research assistant, and web knowledge expert.

Instructions:

1. Use ONLY the supplied context.
2. Do NOT make up information.
3. Combine information from multiple sources when relevant.
4. Provide a natural explanation instead of listing chunks.
5. Explain concepts clearly and in a teaching style.
6. Mention important details when available.
7. If multiple websites contain useful information, synthesize them into one answer.

If the answer does not exist in the context, reply exactly:

I don't know based on the retrieved web pages.

Context:
{context}

Question:
{input}

Answer:
"""
)

def stream_response(chain, query):
    response = chain.invoke({"input":query})
    return response["answer"]

st.set_page_config(page_title="RAG Web Search", layout="wide")

st.title("Web RAG Search (Streaming UI)")
st.write("Ask Questions from the web sources")

with st.sidebar:
    st.sidebar("Settings")
    debug_mode = st.toggle("Debug Retrival")
    k_value = st.slider("Top-K Results", 1, 10, 5)

vectorstore = get_vectorstore()

retriver = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": k_value,
        "fetch_k": 20,
        "lambda_mult": 0.7
    }
)

get_llm = llm()

doc_chain = create_stuff_documents_chain(get_llm, prompt)
retrival_chain = create_retrieval_chain(retriver, doc_chain)

query = st.chat_input(
    "Ask questions from web sources..."
)

if query:
    # Debug retrieval ✅
    if debug_mode:
        st.subheader("🔍 Retrieved Context")
        docs = retriver.get_relevant_documents(query)

        for i, d in enumerate(docs):
            st.markdown(f"**Result {i+1}**")
            st.markdown(f"Source: `{d.metadata.get('source', 'N/A')}`")
            st.write(d.page_content[:300] + "...")
    
    # Streaming output ✅
    st.subheader("🤖 Answer")

    placeholder = st.empty()
    full_response = ""

    # Simulated streaming (Bedrock stream handling workaround)
    result = retrival_chain.invoke({"input": query})
    answer = result["answer"]

    
    for chunk in answer.split():
        full_response += chunk + " "
        placeholder.markdown(full_response)












