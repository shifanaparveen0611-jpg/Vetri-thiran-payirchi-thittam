from pathlib import Path


def build_comic_layout(outline, story, image_paths):

    story_by_num = {
        int(panel.get("panel_number", index + 1)): panel
        for index, panel in enumerate(story)
    }

    layout = []

    for index, outline_panel in enumerate(outline):

        number = int(
            outline_panel.get(
                "panel_number",
                index + 1
            )
        )

        script = story_by_num.get(number, {})

        path = Path(image_paths[index])

        panel = {
            "panel_number": number,

            "title": (
                script.get("title")
                or outline_panel.get(
                    "title",
                    f"Panel {number}"
                )
            ),

            "scene_description": (
                script.get("scene_description")
                or outline_panel.get(
                    "scene_description",
                    ""
                )
            ),

            "image_prompt": outline_panel.get(
                "image_prompt",
                ""
            ),

            "image_path": str(path),

            "image_url": (
                "/static/panels/"
                + path.name
            ),

            "caption": script.get("caption", ""),

            "narration": script.get("narration", ""),

            "dialogue": script.get("dialogue", "")
        }

        layout.append(panel)

    return layout