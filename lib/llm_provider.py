"""
ThinkTank Demo - LLM Provider
Simplified Claude API integration
"""

import anthropic
from lib.config import CLAUDE_API_KEY, CLAUDE_MODEL


def query_llm(prompt, max_tokens=256, model=None):
    """
    Query Claude API with the given prompt.

    Args:
        prompt: User prompt/question
        max_tokens: Maximum tokens in response
        model: Model version (defaults to CLAUDE_MODEL from config)

    Returns:
        str: Model response text
    """
    if not CLAUDE_API_KEY:
        raise ValueError(
            "CLAUDE_API_KEY not set. "
            "Please set it in your .env file or export it as an environment variable."
        )

    try:
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

        response = client.messages.create(
            model=model or CLAUDE_MODEL,
            max_tokens=max_tokens,
            system="You are a helpful AI assistant. Please respond only to the specific question provided.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text

    except Exception as e:
        return f"[Claude API Error] {str(e)}"
