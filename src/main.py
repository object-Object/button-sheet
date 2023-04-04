from pathlib import Path

import numpy as np
import tomllib
from fpdf import FPDF
from PIL import Image

from config import Config, ImageConfig
from draw import background_ellipse, ellipse_mask


def load_image(
    image_config: ImageConfig,
    image_diameter: int,
    margin_width: int,
    border_width: int,
    full_width: int,
) -> Image.Image:
    # load image from file
    im = Image.open(image_config["filename"])
    if im.size[0] != im.size[1]:
        raise Exception(f"{image_config['filename']} is not square: {im.size}")

    # scale image to needed size
    im = im.resize((image_diameter,) * 2)

    # apply mask by taking minimum of im alpha value and mask value
    # this is to account for transparency at edges of im
    mask = np.array(ellipse_mask(im.size))
    na = np.array(im)
    na[..., 3] = np.minimum(na[..., 3], mask)
    im = Image.fromarray(na)
    del na, mask

    # create solid colour background circle and black border
    margin = background_ellipse(
        (image_diameter + 2 * margin_width,) * 2,
        image_config["background"],
    )
    if border_width > 0:
        background = background_ellipse((full_width,) * 2, "#000000")
        background.paste(margin, (border_width,) * 2, margin)
    else:
        background = margin

    # put image over background
    foreground = Image.new("RGBA", (full_width,) * 2, (0,) * 4)
    foreground.paste(im, (margin_width + border_width,) * 2)
    return Image.alpha_composite(background, foreground)


def int_groups(n: int, num_groups: int):
    d, r = divmod(n, num_groups)
    return [d + 1] * r + [d] * (num_groups - r)


def main():
    # load the config that says what to actually generate
    print("Loading config...")
    with open("config.toml", "rb") as f:
        config = Config(**tomllib.load(f))

    # extract sizing from config
    output = config["output"]
    columns = output["columns"]
    rows = output["rows"]
    dpi = output["dpi"]

    page_width_mm = 8.5 * 25.4
    page_height_mm = 11 * 25.4
    px_per_mm = int(dpi / 25.4)

    image_diameter = int(output["image_diameter_mm"] * px_per_mm)
    margin_width = int(output["margin_width_mm"] * px_per_mm)
    border_width = int(output["border_width_mm"] * px_per_mm)
    min_spacing_mm = output["min_spacing_mm"]
    page_margin_mm = output["page_margin_mm"]

    # width of button in px, including solid-colour margin
    full_width = image_diameter + 2 * (margin_width + border_width)
    full_width_mm = full_width / px_per_mm

    # size of the area allotted to a single button
    # includes empty whitespace around the solid-colour margin
    cell_width_mm = (page_width_mm - 2 * page_margin_mm) / columns
    cell_height_mm = (page_height_mm - 2 * page_margin_mm) / rows

    # position of the top left corner of the top left button
    col_offset_mm = (cell_width_mm - full_width_mm) / 2 + page_margin_mm
    row_offset_mm = (cell_height_mm - full_width_mm) / 2 + page_margin_mm

    # make sure there's clearance between buttons
    worst_spacing_mm = min(cell_width_mm, cell_height_mm) - full_width_mm
    if worst_spacing_mm < min_spacing_mm:
        raise Exception(
            f"Buttons are too close together (want {min_spacing_mm}, got {worst_spacing_mm})"
        )

    # load all the images, process them, and save the processed versions to disk
    print("Processing images...")
    images: dict[str, str] = {}
    Path("build").mkdir(exist_ok=True)
    for key, image_config in config["images"].items():
        filename = f"build/{key}.png"
        load_image(
            image_config,
            image_diameter,
            margin_width,
            border_width,
            full_width,
        ).save(filename)
        images[key] = filename

    buttons_per_page = columns * rows
    pdf = FPDF("P", "mm", (page_width_mm, page_height_mm))

    # generate all the pages
    for i, page_keys in enumerate(output["pages"]):
        # ensure we can actually fit all the buttons we want to
        print(f"Generating page {i + 1}/{len(output['pages'])}...")
        if len(page_keys) > buttons_per_page:
            raise Exception(
                f"Too many buttons (need <={buttons_per_page}, got {len(page_keys)}): {page_keys}"
            )

        # create new pdf page
        pdf.add_page()
        pdf.set_margins(page_margin_mm, page_margin_mm, page_margin_mm)

        # add a roughly equal amount of each button
        column, row = 0, 0
        for count, key in zip(int_groups(buttons_per_page, len(page_keys)), page_keys):
            for _ in range(count):
                # paste the current button onto the page
                pdf.image(
                    images[key],
                    x=column * cell_width_mm + col_offset_mm,
                    y=row * cell_height_mm + row_offset_mm,
                    w=full_width_mm,
                    h=full_width_mm,
                )

                # move to the next position
                column += 1
                if column >= columns:
                    column = 0
                    row += 1

    # save the completed pdf
    print("Writing pdf...")
    pdf.output("buttons.pdf")
    print("Done.")


if __name__ == "__main__":
    main()
