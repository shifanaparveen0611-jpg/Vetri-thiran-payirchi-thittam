import json
import re

from app.config import (
    GEMINI_API_KEY,
    GEMINI_OUTLINE_MODEL,
    ALLOW_DEMO_MODE
)


def _demo_outline(
    prompt,
    character_name,
    setting,
    tone,
    art_style,
    count
):

    titles = [
        "A Curious Beginning",
        "The Unexpected Clue",
        "A Difficult Choice",
        "The Big Moment",
        "A New Beginning",
        "One Last Surprise"
    ]

    stages = [
        (
            f"{character_name} begins the adventure "
            f"after hearing about this mystery: {prompt}"
        ),
        (
            f"In {setting}, {character_name} discovers "
            "a clue that changes everything."
        ),
        (
            "The challenge becomes serious, and "
            f"{character_name} must choose how to respond."
        ),
        (
            f"{character_name} puts the plan into action "
            "in a dramatic turning point."
        ),
        (
            f"The adventure reaches a satisfying resolution "
            "with a lesson learned."
        ),
        (
            "A small surprise hints that another "
            "adventure may be waiting."
        )
    ]

    panels = []

    for index in range(count):

        scene = stages[index]

        panels.append({
            "panel_number": index + 1,
            "title": titles[index],
            "scene_description": scene,
            "image_prompt": (
                f"{art_style} illustration, "
                f"{tone} mood, "
                f"{character_name}, {setting}, "
                f"scene: {scene}, "
                "consistent character design, "
                "expressive composition, clean line art, "
                "no text, no watermark"
            )
        })

    return panels


def generate_outline(
    prompt,
    character_name="Alex",
    setting="enchanted forest",
    tone="adventurous",
    art_style="comic book",
    count=5
):

    if not GEMINI_API_KEY:

        if ALLOW_DEMO_MODE:

            return _demo_outline(
                prompt,
                character_name,
                setting,
                tone,
                art_style,
                count
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

        instruction = f"""
Create exactly {count} connected comic panels.

User idea: {prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY a valid JSON array.

Each item must contain:
- panel_number: integer
- title: short string
- scene_description: maximum two sentences
- image_prompt: visual prompt for an image model

Keep the character and setting consistent.
Do not put lettering inside the image prompt.
"""

        response = client.models.generate_content(
            model=GEMINI_OUTLINE_MODEL,
            contents=instruction
        )

        raw = response.text or ""

        raw = re.sub(
            r"^\s*```(?:json)?\s*|\s*```\s*$",
            "",
            raw,
            flags=re.I
        )

        data = json.loads(raw)

        if (
            not isinstance(data, list)
            or len(data) < count
        ):

            raise ValueError(
                "Gemini returned an invalid panel outline."
            )

        return data[:count]

    except Exception as exc:

        if ALLOW_DEMO_MODE:

            return _demo_outline(
                prompt,
                character_name,
                setting,
                tone,
                art_style,
                count
            )

        raise RuntimeError(
            f"Gemini outline generation failed: {exc}"
        ) from exc