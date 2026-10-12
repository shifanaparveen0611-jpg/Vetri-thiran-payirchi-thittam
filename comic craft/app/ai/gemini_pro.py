import json
import re

from app.config import (
    GEMINI_API_KEY,
    GEMINI_STORY_MODEL,
    ALLOW_DEMO_MODE
)


def _demo_story(
    outline,
    character_name,
    tone
):

    result = []

    for panel in outline:

        result.append({
            "panel_number": panel["panel_number"],

            "title": panel["title"],

            "scene_description": (
                panel["scene_description"]
            ),

            "caption": (
                f"The {tone} adventure continues..."
            ),

            "narration": (
                f"{character_name} takes a deep breath "
                "and moves forward. Every clue brings "
                "the story closer to its conclusion."
            ),

            "dialogue": (
                f'{character_name}: '
                '"We can do this, one step at a time!"'
            )
        })

    return result


def generate_story(
    outline,
    character_name="Alex",
    tone="adventurous"
):

    if not GEMINI_API_KEY:

        if ALLOW_DEMO_MODE:

            return _demo_story(
                outline,
                character_name,
                tone
            )

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    try:

        from google import genai

        client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        prompt = f"""
Expand this outline into a coherent comic script.

Main character: {character_name}
Tone: {tone}

Return ONLY a JSON array with one object per panel.

Every object must contain:
- panel_number
- title
- scene_description
- caption
- narration
- dialogue

Preserve the panel numbers and titles.
Keep narration concise and dialogue natural.

Outline:
{json.dumps(outline, ensure_ascii=False)}
"""

        response = client.models.generate_content(
            model=GEMINI_STORY_MODEL,
            contents=prompt
        )

        raw = re.sub(
            r"^\s*```(?:json)?\s*|\s*```\s*$",
            "",
            response.text or "",
            flags=re.I
        )

        data = json.loads(raw)

        if not isinstance(data, list):

            raise ValueError(
                "Gemini returned an invalid story."
            )

        by_num = {
            int(item.get("panel_number", index + 1)): item
            for index, item in enumerate(data)
        }

        return [
            by_num.get(
                int(panel["panel_number"]),
                panel
            )
            for panel in outline
        ]

    except Exception:

        if ALLOW_DEMO_MODE:

            return _demo_story(
                outline,
                character_name,
                tone
            )

        raise