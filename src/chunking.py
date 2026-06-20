from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

def get_transcript(video_id: str):
    """Takes in video_id of the youtube video and returns its transcript."""
    try:
        ytt_api = YouTubeTranscriptApi()

        # If you don't care which language, this returns the "best" one
        fetched_transcript = ytt_api.fetch(video_id, languages=["en"])

        # Flatten it to plain text
        return " ".join(snippet.text for snippet in fetched_transcript)

    except TranscriptsDisabled:
        print("No captions available for this video")
        return None
    
if __name__ == "__main__":
    video_id = "v1wZwxY3CMg"
    transcript = get_transcript(video_id)

    print(transcript)