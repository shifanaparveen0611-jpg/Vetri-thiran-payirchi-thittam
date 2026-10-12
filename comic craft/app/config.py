import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")

APP_NAME = "ComicCraft"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

GEMINI_OUTLINE_MODEL = os.getenv(
    "GEMINI_OUTLINE_MODEL",
    "gemini-2.5-flash"
)

GEMINI_STORY_MODEL = os.getenv(
    "GEMINI_STORY_MODEL",
    "gemini-2.5-flash"
)

HF_API_TOKEN = os.getenv("HF_API_TOKEN", "").strip()

HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL",
    "stabilityai/stable-diffusion-xl-base-1.0"
)

IMAGE_PROVIDER = os.getenv(
    "IMAGE_PROVIDER",
    "huggingface"
).lower()

ALLOW_DEMO_MODE = os.getenv(
    "ALLOW_DEMO_MODE",
    "true"
).lower() in {"1", "true", "yes"}

PANELS_DIR = ROOT_DIR / "static" / "panels"

EXPORTS_DIR = ROOT_DIR / "static" / "exports"