import streamlit as st
from backend import get_video_id, build_retriever, stream_answer

st.set_page_config(page_title="YouTube RAG Chatbot", page_icon="🎥", layout="wide")

# Session state setup
if "video_id" not in st.session_state:
    st.session_state.video_id = None
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "video_url" not in st.session_state:
    st.session_state.video_url = ""
if "error" not in st.session_state:
    st.session_state.error = None


@st.cache_resource(show_spinner=False)
def get_cached_retriever(video_id: str):
    """Cached wrapper so the same video is never reprocessed across reruns/sessions."""
    return build_retriever(video_id)


def process_video(url: str):
    """Resolve a URL to a video_id and (re)build the retriever if needed."""
    st.session_state.error = None
    try:
        video_id = get_video_id(url)
    except Exception as e:
        st.session_state.error = f"Couldn't extract a video ID from that URL: {e}"
        return

    if not video_id:
        st.session_state.error = "That doesn't look like a valid YouTube URL."
        return

    # Skip rebuilding if it's the same video already loaded
    if video_id == st.session_state.video_id and st.session_state.retriever is not None:
        return

    try:
        with st.spinner("Fetching transcript and building index..."):
            retriever = get_cached_retriever(video_id)
    except Exception as e:
        st.session_state.error = (
            f"Couldn't process this video. It may not have captions available, "
            f"or another error occurred:\n\n{e}"
        )
        st.session_state.video_id = None
        st.session_state.retriever = None
        return

    st.session_state.video_id = video_id
    st.session_state.retriever = retriever
    st.session_state.video_url = url


# Sidebar — video input
with st.sidebar:
    st.header("🎥 Load a video")
    url_input = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    load_clicked = st.button("Load video", type="primary", use_container_width=True)

    if load_clicked:
        if not url_input.strip():
            st.session_state.error = "Please enter a YouTube URL first."
        else:
            process_video(url_input.strip())

    if st.session_state.error:
        st.error(st.session_state.error)

    if st.session_state.video_id:
        st.success("Video loaded ✅")
        st.video(st.session_state.video_url or f"https://www.youtube.com/watch?v={st.session_state.video_id}")


# Main area — single Q&A
st.title("YouTube RAG Chatbot")
st.caption("Ask a question about the loaded video's transcript.")

if not st.session_state.retriever:
    st.info("Load a video from the sidebar to get started.")
else:
    question = st.text_input("Your question", placeholder="What is this video about?")
    ask_clicked = st.button("Ask", type="primary")

    if ask_clicked:
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            st.markdown("### Answer")
            try:
                response_container = st.empty()
                full_response = ""
                for chunk in stream_answer(st.session_state.retriever, question):
                    full_response += chunk
                    response_container.markdown(full_response)
            except Exception as e:
                st.error(f"Something went wrong while generating the answer: {e}")