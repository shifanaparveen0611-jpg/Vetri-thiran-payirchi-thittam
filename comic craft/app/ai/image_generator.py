import io
import uuid

import requests

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import (
    HF_API_TOKEN,
    HF_IMAGE_MODEL,
    IMAGE_PROVIDER,
    PANELS_DIR,
    ALLOW_DEMO_MODE
)


def _placeholder(prompt, destination):

    width = 1024
    height = 640

    image = Image.new(
        "RGB",
        (width, height),
        "#f1e8ff"
    )

    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (28, 28, width - 28, height - 28),
        radius=28,
        outline="#5d3a8a",
        width=8
    )

    draw.ellipse(
        (width - 210, 55, width - 95, 170),
        fill="#ffd166",
        outline="#5d3a8a",
        width=4
    )

    draw.polygon(
        [(60, 510), (300, 230), (500, 510)],
        fill="#b7d7b0",
        outline="#315c45"
    )

    draw.polygon(
        [(350, 510), (650, 190), (960, 510)],
        fill="#92b4de",
        outline="#315c45"
    )

    try:

        font = ImageFont.truetype(
            "DejaVuSans.ttf",
            30
        )

        small_font = ImageFont.truetype(
            "DejaVuSans.ttf",
            19
        )

    except Exception:

        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.text(
        (65, 65),
        "COMICCRAFT - DEMO ART",
        fill="#392653",
        font=font
    )

    words = prompt[:110]

    draw.text(
        (65, 555),
        words,
        fill="#392653",
        font=small_font
    )

    image.save(
        destination,
        "PNG"
    )

    return destination


def generate_image(
    prompt,
    panel_number=1
):

    PANELS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    destination = PANELS_DIR / (
        f"panel_{panel_number}_"
        f"{uuid.uuid4().hex[:8]}.png"
    )

    # Try live Hugging Face image generation
    if (
        IMAGE_PROVIDER == "huggingface"
        and HF_API_TOKEN
    ):

        try:

            endpoint = (
                "https://router.huggingface.co/"
                f"hf-inference/models/{HF_IMAGE_MODEL}"
            )

            response = requests.post(
                endpoint,
                headers={
                    "Authorization": (
                        f"Bearer {HF_API_TOKEN}"
                    ),
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": prompt,
                    "options": {
                        "wait_for_model": True
                    }
                },
                timeout=180
            )

            response.raise_for_status()

            content_type = response.headers.get(
                "content-type",
                ""
            )

            if "image" not in content_type:

                raise RuntimeError(
                    "Image service returned an unexpected "
                    f"content type: {content_type}"
                )

            image = Image.open(
                io.BytesIO(response.content)
            ).convert("RGB")

            image.save(
                destination,
                "PNG"
            )

            return destination

        except Exception as exc:

            if not ALLOW_DEMO_MODE:

                raise RuntimeError(
                    "Hugging Face image generation failed: "
                    f"{exc}"
                ) from exc

    elif not ALLOW_DEMO_MODE:

        raise RuntimeError(
            "Set HF_API_TOKEN in .env "
            "to enable image generation."
        )

    # Local demo illustration
    return _placeholder(
        prompt,
        destination
    )