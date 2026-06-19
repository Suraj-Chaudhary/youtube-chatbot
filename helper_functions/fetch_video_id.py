import re
from urllib.parse import urlparse, parse_qs

def get_youtube_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    Supports formats like:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
      - https://www.youtube.com/embed/VIDEO_ID
      - https://www.youtube.com/shorts/VIDEO_ID
      - https://m.youtube.com/watch?v=VIDEO_ID
    Returns the video ID as a string, or None if not found.
    """
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""

    # youtu.be short links
    if "youtu.be" in hostname:
        return parsed_url.path.lstrip("/")

    if "youtube.com" in hostname:
        # Standard watch URL: ?v=VIDEO_ID
        if parsed_url.path == "/watch":
            query = parse_qs(parsed_url.query)
            return query.get("v", [None])[0]

        # Embed or shorts URLs: /embed/VIDEO_ID or /shorts/VIDEO_ID
        match = re.match(r"^/(embed|shorts|v)/([^/?]+)", parsed_url.path)
        if match:
            return match.group(2)

    return None


if __name__ == "__main__":
    # Example usage
    urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s",
    ]

    for u in urls:
        print(u, "->", get_youtube_video_id(u))