from pathlib import Path
from datetime import datetime

from fpdf import FPDF
from PIL import Image

from app.config import EXPORTS_DIR


def save_pdf(layout, character_name="ComicCraft"):

    EXPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_name = "".join(
        character.lower()
        if character.isalnum()
        else "_"
        for character in character_name
    ).strip("_") or "comic"

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output = EXPORTS_DIR / (
        f"{safe_name}_{timestamp}.pdf"
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    for panel in layout:

        pdf.add_page()

        # Panel title
        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        title = str(
            panel.get(
                "title",
                "Comic Panel"
            )
        )

        pdf.multi_cell(
            0,
            10,
            title.encode(
                "latin-1",
                "replace"
            ).decode("latin-1")
        )

        # Panel illustration
        image_path = Path(
            panel["image_path"]
        )

        if image_path.exists():

            with Image.open(image_path) as image:

                image_width, image_height = image.size

            max_width = 180
            max_height = 105

            scale = min(
                max_width / image_width,
                max_height / image_height
            )

            width = image_width * scale
            height = image_height * scale

            pdf.image(
                str(image_path),
                x=(210 - width) / 2,
                y=35,
                w=width,
                h=height
            )

        pdf.set_y(150)

        sections = [
            ("Scene", "scene_description"),
            ("Caption", "caption"),
            ("Narration", "narration"),
            ("Dialogue", "dialogue")
        ]

        for label, key in sections:

            value = str(
                panel.get(key, "") or ""
            )

            if value:

                pdf.set_font(
                    "Helvetica",
                    "B",
                    11
                )

                pdf.cell(
                    0,
                    7,
                    label,
                    ln=1
                )

                pdf.set_font(
                    "Helvetica",
                    "",
                    10
                )

                pdf.multi_cell(
                    0,
                    6,
                    value.encode(
                        "latin-1",
                        "replace"
                    ).decode("latin-1")
                )

                pdf.ln(2)

    pdf.output(str(output))

    return output