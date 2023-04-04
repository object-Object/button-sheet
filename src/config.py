from typing import TypedDict


class ImageConfig(TypedDict):
    filename: str
    background: str


class OutputConfig(TypedDict):
    rows: int
    columns: int

    px_per_mm: int

    image_diameter_mm: float
    margin_width_mm: float
    border_width_mm: float
    min_spacing_mm: float
    page_margin_mm: float

    pages: list[list[str]]


class Config(TypedDict):
    images: dict[str, ImageConfig]
    output: OutputConfig
