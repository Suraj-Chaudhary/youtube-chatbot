from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from src.chunking import get_transcript
from src.embedding import embed_and_retrieve, format_docs
from src.augment import _prompt_template
from helper_functions.fetch_video_id import get_youtube_video_id

load_dotenv()
model = ChatAnthropic(model = "claude-haiku-4-5-20251001", temperature = 0.3)

url = input("Enter video url:")
video_id = get_youtube_video_id(url)
transcript = get_transcript(video_id)

retriever = embed_and_retrieve(transcript)

prompt = _prompt_template()

question = input("What is your question?")
retrieved_docs = retriever.invoke(question)

parallel_chain = RunnableParallel({
    "context": retriever | RunnableLambda(format_docs),
    "question": RunnablePassthrough()
})

parser = StrOutputParser()

main_chain = parallel_chain | prompt | model | parser

main_chain.invoke(question)