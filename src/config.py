from typing import TypedDict


class ImageConfig(TypedDict):
    filename: str
    background: str


class OutputConfig(TypedDict):
    rows: int
    columns: int

    image_diameter_mm: int
    margin_width_mm: int
    min_spacing_mm: int
    page_margin_mm: int

    pages: list[list[str]]


class Config(TypedDict):
    images: dict[str, ImageConfig]
    output: OutputConfig
