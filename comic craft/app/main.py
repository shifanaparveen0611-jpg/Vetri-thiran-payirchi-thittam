from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import router


BASE_DIR = Path(__file__).resolve().parent.parent

# Create folders automatically
(BASE_DIR / "static" / "panels").mkdir(
    parents=True,
    exist_ok=True
)

(BASE_DIR / "static" / "exports").mkdir(
    parents=True,
    exist_ok=True
)

# Create FastAPI application
app = FastAPI(
    title="ComicCraft",
    description="AI-powered comic story creator",
    version="1.0.0"
)

# Serve CSS and generated images
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

# Configure HTML templates
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

app.state.templates = templates

# Register application routes
app.include_router(router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ComicCraft"
    }