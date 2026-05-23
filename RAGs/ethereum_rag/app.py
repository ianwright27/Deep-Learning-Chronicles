import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama


# load the PDF document
loader = PyPDFLoader("docs/introduction-to-ethereum.pdf")
docs = loader.load()

# split text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
splits = text_splitter.split_documents(docs)

# create embeddings
embeddings = OllamaEmbeddings(model="qwen2.5:3b")

# Store in Chroma vector database 
from chromadb.config import Settings
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="chroma_db",
    client_settings=Settings(
        anonymized_telemetry=False
    )
)

# user query 
query = "What is Ethereum?"

# retrieve rlevant chunks
retriever = vectorstore.as_retriever()
relevant_docs = retriever.invoke(query)

# Local LLM
llm = ChatOllama(model="qwen2.5:3b")

# Build prompt 
context = "\n\n".join([doc.page_content for doc in relevant_docs]) 

prompt = f"""
Answer the question using the context below. 

Context:
{context}

Question:
{query}
"""

# Generate a response
response = llm.invoke(prompt)

print("\nANSWER:\n")
print(response.content)