"""
Part 3: Transform Transcripts into Magazine Articles using an LLM
Anthropic-compatible HTTP API: either a custom proxy (ANTHROPIC_BASE_URL) or ModelScope.
"""

import os
from typing import Optional

import anthropic
from dotenv import load_dotenv

load_dotenv()

# Proxy / Claude Code–style stack (takes precedence when ANTHROPIC_BASE_URL is set)
_ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
_ANTHROPIC_KEY = os.getenv("ANTHROPIC_AUTH_TOKEN") or os.getenv("ANTHROPIC_API_KEY")

# ModelScope fallback
_MODELSCOPE_BASE_URL = os.getenv(
    "MODELSCOPE_BASE_URL", "https://api-inference.modelscope.cn"
)

if _ANTHROPIC_BASE_URL:
    _LLM_BASE_URL = _ANTHROPIC_BASE_URL.rstrip("/")
    _LLM_API_KEY = _ANTHROPIC_KEY
    _LLM_MODEL = os.getenv("ANTHROPIC_MODEL") or "glm-5"
else:
    _LLM_BASE_URL = _MODELSCOPE_BASE_URL.rstrip("/")
    _LLM_API_KEY = os.getenv("MODELSCOPE_API_KEY")
    _LLM_MODEL = os.getenv("MODELSCOPE_MODEL") or "ZhipuAI/GLM-4.7-Flash"

_client: Optional[anthropic.Anthropic] = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is not None:
        return _client
    if not _LLM_API_KEY:
        if _ANTHROPIC_BASE_URL:
            raise RuntimeError(
                "ANTHROPIC_BASE_URL is set but no API key: set ANTHROPIC_AUTH_TOKEN "
                "(or ANTHROPIC_API_KEY) in .env."
            )
        raise RuntimeError(
            "No LLM API key: set MODELSCOPE_API_KEY for ModelScope, or "
            "ANTHROPIC_BASE_URL + ANTHROPIC_AUTH_TOKEN for an Anthropic-compatible proxy."
        )
    _client = anthropic.Anthropic(
        base_url=_LLM_BASE_URL,
        api_key=_LLM_API_KEY,
    )
    return _client


def write_article(video):
    """
    Use the configured LLM to transform a video transcript into a magazine-style article.
    """
    prompt = f"""You are a skilled magazine writer. Transform this YouTube video transcript into a well-written, engaging article.

VIDEO TITLE: {video['title']}
CHANNEL: {video['channel']}
VIDEO URL: {video['url']}

VIDEO DESCRIPTION:
{video['description']}

TRANSCRIPT:
{video['transcript']}

---

Remix this YouTube transcript into a magazine article. Guidelines:
- Use the video title and description to correct any transcription errors, especially names of people, companies, or technical terms. The description often contains the correct spellings.
- Start with an engaging headline (different from the video title)
- The audience is a curious individual who is generally smart but not a specialist or expert in the area mentioned in the video
- Highly engaging and readable. Wherever jargon or obscure references appear, explain them. Extremely well-written; think New Yorker or the Atlantic
- Capture the key insights, especially contrarian viewpoints, memorable anecdotes, and surprising insights. Preserve key quotes (clean up filler words or transcription errors).
- There's no fixed length requirement; it depends on the length of the original article as well as the insight density. Make your own judgment. This should be a satisfying long-read.
- Do NOT include phrases like "In this video" - write it as a standalone article. Assume the reader has not watched the video and has zero context about it. This article is meant to be as a replacement, not complement, for watching the video.

Format the article in clean markdown."""

    try:
        client = _get_client()
        message = client.messages.create(
            model=_LLM_MODEL,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
        )
        parts: list[str] = []
        for block in message.content:
            if block.type == "text":
                parts.append(block.text)
        text = "".join(parts)
        return text if text.strip() else None

    except RuntimeError as e:
        print(f"  ⚠ {e}")
        return None
    except Exception as e:
        print(f"  ⚠ Error generating article: {e}")
        return None


def write_articles_for_videos(videos):
    """
    Generate articles for all videos with transcripts.
    """
    print("\nGenerating articles via LLM (Anthropic-compatible API)...\n")
    print("=" * 60)

    articles = []

    for video in videos:
        print(f"Writing article: {video['title'][:50]}...")

        article = write_article(video)

        if article:
            articles.append({
                "title": video["title"],
                "channel": video["channel"],
                "url": video["url"],
                "article": article
            })
            print(f"  ✓ Article generated!\n")
        else:
            print(f"  ✗ Failed to generate article\n")

    print("=" * 60)
    print(f"Generated {len(articles)} articles")

    return articles


# Test it standalone
if __name__ == "__main__":
    # Test with a mock video
    test_video = {
        "title": "Test Video",
        "channel": "Test Channel",
        "url": "https://youtube.com/watch?v=test",
        "description": "",
        "transcript": "Hello everyone, today we're going to talk about something really exciting. I've been working on this project for months and I can't wait to share it with you. The main idea is simple but powerful..."
    }

    print("Testing article generation...")
    article = write_article(test_video)
    if article:
        print("\nGenerated article:\n")
        print(article)
