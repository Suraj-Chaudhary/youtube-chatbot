from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from src.chunking import get_transcript
from src.embedding import embed_and_retrieve, format_docs
from src.augment import _prompt_template
from helper_functions.fetch_video_id import get_youtube_video_id

load_dotenv()

def get_video_id(url: str) -> str:
    """Extract the YouTube video ID from a URL."""
    return get_youtube_video_id(url)


def build_retriever(video_id: str):
    """Fetch the transcript for a video_id and build a FAISS retriever from it."""
    transcript = get_transcript(video_id)
    retriever = embed_and_retrieve(transcript)
    # retriever = vectorstore.as_retriever(search_type = "similarity", search_kwargs = {"k":4})
    return retriever


def build_chain(retriever):
    """Assemble the full RAG chain: retrieval -> prompt -> model -> parser."""
    parallel_chain = RunnableParallel({
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    })

    prompt = _prompt_template()
    model = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0.3)
    parser = StrOutputParser()

    return parallel_chain | prompt | model | parser


def stream_answer(retriever, question: str):
    """Build the chain for a given retriever and stream the answer to a question.
    Yields string chunks as they arrive from the model.
    """
    chain = build_chain(retriever)
    for chunk in chain.stream(question):
        yield chunk