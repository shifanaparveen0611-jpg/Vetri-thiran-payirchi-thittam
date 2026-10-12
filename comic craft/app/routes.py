from pathlib import Path

from fastapi import (
    APIRouter,
    Request,
    Form,
    HTTPException
)

from fastapi.responses import (
    HTMLResponse,
    FileResponse,
    JSONResponse
)

from app.schemas import PromptRequest

from app.ai.gemini_flash import generate_outline
from app.ai.gemini_pro import generate_story
from app.ai.image_generator import generate_image

from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

from app.config import ROOT_DIR, ALLOW_DEMO_MODE


router = APIRouter()


def get_templates(request):
    return request.app.state.templates


def create_comic(data: PromptRequest):

    # Generate the comic outline
    outline = generate_outline(
        data.prompt,
        data.character_name,
        data.setting,
        data.tone,
        data.art_style,
        data.panels
    )

    # Generate the comic script
    story = generate_story(
        outline,
        data.character_name,
        data.tone
    )

    image_paths = []

    # Generate an illustration for every panel
    for panel in outline:

        image_prompt = panel.get(
            "image_prompt",
            panel.get("scene_description", "")
        )

        if not data.generate_images:
            image_prompt = (
                "Comic preview illustration: "
                + panel.get("title", "Comic panel")
            )

        image_path = generate_image(
            image_prompt,
            panel.get("panel_number", 1)
        )

        image_paths.append(image_path)

    # Combine story and illustrations
    layout = build_comic_layout(
        outline,
        story,
        image_paths
    )

    # Export the comic as a PDF
    pdf_path = save_pdf(
        layout,
        data.character_name
    )

    return layout, pdf_path


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return get_templates(request).TemplateResponse(
        request=request,
        name="index.html",
        context={
            "demo_mode": ALLOW_DEMO_MODE
        }
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_form(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form("Alex"),
    setting: str = Form("enchanted forest"),
    tone: str = Form("adventurous"),
    art_style: str = Form("comic book"),
    panels: int = Form(5)
):

    try:

        data = PromptRequest(
            prompt=prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
            panels=panels
        )

        layout, pdf_path = create_comic(data)

        return get_templates(request).TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_url": f"/download/{pdf_path.name}",
                "character_name": data.character_name
            }
        )

    except Exception as exc:

        return get_templates(request).TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc),
                "demo_mode": ALLOW_DEMO_MODE,
                "form": {
                    "prompt": prompt,
                    "character_name": character_name,
                    "setting": setting,
                    "tone": tone,
                    "art_style": art_style,
                    "panels": panels
                }
            },
            status_code=400
        )


@router.post("/generate-comic/json")
async def generate_json(data: PromptRequest):

    try:

        layout, pdf_path = create_comic(data)

        serializable = []

        for panel in layout:

            item = dict(panel)

            item["image_path"] = str(
                Path(
                    panel["image_path"]
                ).relative_to(ROOT_DIR)
            )

            serializable.append(item)

        return JSONResponse({
            "status": "success",
            "layout": serializable,
            "pdf_url": f"/download/{pdf_path.name}"
        })

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.post("/test-image")
async def test_image(request: Request):

    try:

        payload = await request.json()

        prompt = str(
            payload.get(
                "prompt",
                "A friendly dragon in comic book style"
            )
        )[:1000]

        path = generate_image(prompt, 99)

        return {
            "status": "success",
            "image_url": f"/static/panels/{path.name}"
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@router.get("/download/{filename}")
async def download_pdf(filename: str):

    # Prevent directory traversal
    if (
        Path(filename).name != filename
        or not filename.endswith(".pdf")
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    path = ROOT_DIR / "static" / "exports" / filename

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail="PDF not found"
        )

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):

    return get_templates(request).TemplateResponse(
        request=request,
        name="export_success.html",
        context={}
    )