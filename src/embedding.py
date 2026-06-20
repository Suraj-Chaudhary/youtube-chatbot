from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()
splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)
embeddings = HuggingFaceEmbeddings(model = "sentence-transformers/all-MiniLM-L6-v2")

def embed_and_retrieve(transcript):
    "Takes in transcript of the youtube video and returns the retriever runnable object."
    chunks = splitter.create_documents([transcript])
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_type = "similarity", search_kwargs = {"k":4})
    return retriever

def format_docs(retrieved_docs: list) -> str:
    "Takes in list of documents retrieved by the retriever, compiles all the documents into a string and returns it."
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    return context_text