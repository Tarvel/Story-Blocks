"""
engine/services.py

AI Co-Pilot service powered by Groq API.
Provides story enhancement, choice suggestion, and scene expansion.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# System prompts tailored for interactive fiction writing
SYSTEM_PROMPTS = {
    'enhance': (
        "You are a master literary editor specializing in interactive fiction. "
        "Your task is to enhance the descriptive quality and atmosphere of the "
        "given passage. Improve sensory details, pacing, and emotional resonance. "
        "Maintain the original plot points and character voice. "
        "Return ONLY the enhanced passage text, nothing else."
    ),
    'choices': (
        "You are an interactive fiction designer. Given a story passage, "
        "suggest exactly 3 compelling choices the player could make at this point. "
        "Each choice should lead to meaningfully different outcomes. "
        "Format your response as a numbered list:\n"
        "1. [Choice text here]\n"
        "2. [Choice text here]\n"
        "3. [Choice text here]\n"
        "Return ONLY the numbered list, no extra commentary."
    ),
    'expand': (
        "You are a creative fiction writer specializing in interactive narratives. "
        "Continue the given passage with one additional paragraph that advances "
        "the scene naturally. Match the existing tone, style, and pacing. "
        "End the paragraph at a point that creates tension or invites a decision. "
        "Return ONLY the continuation paragraph, nothing else."
    ),
}


def generate_story_enhancement(text_prompt, action_type):
    """
    Call the Groq API to assist with story writing.

    Args:
        text_prompt: The current passage text to work with.
        action_type: One of 'enhance', 'choices', or 'expand'.

    Returns:
        str: The AI-generated text, or an error message.
    """
    if action_type not in SYSTEM_PROMPTS:
        return f"Unknown action type: {action_type}"

    api_key = settings.GROQ_API_KEY
    if not api_key:
        return (
            "⚠ GROQ_API_KEY not set. Add it to your environment variables.\n"
            "export GROQ_API_KEY='your-key-here'"
        )

    try:
        from groq import Groq

        client = Groq(api_key=api_key)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPTS[action_type],
                },
                {
                    "role": "user",
                    "content": text_prompt,
                },
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9,
        )

        return chat_completion.choices[0].message.content.strip()

    except ImportError:
        return (
            "⚠ The 'groq' Python package is not installed.\n"
            "Run: pip install groq"
        )
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return f"⚠ AI Service Error: {str(e)}"
