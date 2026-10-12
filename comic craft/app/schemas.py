from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):

    prompt: str = Field(
        min_length=5,
        max_length=1200
    )

    character_name: str = Field(
        default="Alex",
        min_length=1,
        max_length=60
    )

    setting: str = Field(
        default="enchanted forest",
        max_length=100
    )

    tone: str = Field(
        default="adventurous",
        max_length=40
    )

    art_style: str = Field(
        default="comic book",
        max_length=60
    )

    panels: int = Field(
        default=5,
        ge=3,
        le=6
    )

    generate_images: bool = True

    @field_validator(
        "prompt",
        "character_name",
        "setting",
        "tone",
        "art_style"
    )
    @classmethod
    def strip_strings(cls, value):
        return value.strip()