# file: index_property_info.py
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

# Load and split property text
loader = TextLoader("villa_azul.txt")
docs = loader.load()

# Attach property_id metadata BEFORE splitting so it propagates to all chunks
for doc in docs:
    doc.metadata["property_id"] = "p1"  # <-- join key to bookings.json

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = splitter.split_documents(docs)

# Embed and save to vectorstore using HuggingFace embeddings
# This is compatible with Claude migration since Claude doesn't provide embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(split_docs, embedding=embeddings, persist_directory="chroma_db")
vectorstore.persist()
print("✅ Property info indexed to vector store with HuggingFace embeddings.")