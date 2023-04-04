import numpy as np
import tomllib
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
    background = background_ellipse((full_width,) * 2, "#000000")
    margin = background_ellipse(
        (image_diameter + 2 * margin_width,) * 2,
        image_config["background"],
    )
    background.paste(margin, (border_width,) * 2, margin)

    # put image over background
    foreground = Image.new("RGBA", (full_width,) * 2, (0,) * 4)
    foreground.paste(im, (margin_width + border_width,) * 2)
    return Image.alpha_composite(background, foreground)


def int_groups(n: int, num_groups: int):
    d, r = divmod(n, num_groups)
    return [d + 1] * r + [d] * (num_groups - r)


def main():
    # load the config that says what to actually generate
    with open("config.toml", "rb") as f:
        config = Config(**tomllib.load(f))

    # extract sizing from config
    output = config["output"]
    columns = output["columns"]
    rows = output["rows"]
    px_per_mm = output["px_per_mm"]

    image_diameter = int(output["image_diameter_mm"] * px_per_mm)
    margin_width = int(output["margin_width_mm"] * px_per_mm)
    border_width = int(output["border_width_mm"] * px_per_mm)
    min_spacing = int(output["min_spacing_mm"] * px_per_mm)
    page_margin = int(output["page_margin_mm"] * px_per_mm)

    pdf_dpi = 25.4 * px_per_mm
    pdf_width_px = int(8.5 * pdf_dpi)
    pdf_height_px = int(11 * pdf_dpi)

    # width of button in px, including solid-colour margin
    full_width = image_diameter + 2 * (margin_width + border_width)

    # size of the area allotted to a single button
    # includes empty whitespace around the solid-colour margin
    cell_width = (pdf_width_px - 2 * page_margin) // columns
    cell_height = (pdf_height_px - 2 * page_margin) // rows

    # position of the top left corner of the top left button
    col_offset = (cell_width - full_width) // 2 + page_margin
    row_offset = (cell_height - full_width) // 2 + page_margin

    # make sure there's clearance between buttons
    worst_spacing = min(cell_width, cell_height) - full_width
    if worst_spacing < min_spacing:
        raise Exception(
            f"Buttons are too close together (want {min_spacing}, got {worst_spacing})"
        )

    # load all the images from files
    images = {
        k: load_image(i, image_diameter, margin_width, border_width, full_width)
        for k, i in config["images"].items()
    }

    buttons_per_page = columns * rows
    pdf_pages: list[Image.Image] = []

    # generate all the pages
    for page_keys in output["pages"]:
        # ensure we can actually fit all the buttons we want to
        if len(page_keys) > buttons_per_page:
            raise Exception(
                f"Too many buttons (need <={buttons_per_page}, got {len(page_keys)}): {page_keys}"
            )

        # create new pdf page
        page = Image.new("RGB", (pdf_width_px, pdf_height_px), (255,) * 4)
        column, row = 0, 0

        # add a roughly equal amount of each button
        for count, key in zip(int_groups(buttons_per_page, len(page_keys)), page_keys):
            image = images[key]
            for _ in range(count):
                # paste the current button onto the page
                box = (
                    column * cell_width + col_offset,
                    row * cell_height + row_offset,
                )
                page.paste(image, box, image)

                # move to the next position
                column += 1
                if column >= columns:
                    column = 0
                    row += 1

        # add the finished page to the list
        pdf_pages.append(page)

    # save all pages in a single pdf by saving the first one and appending the rest
    pdf_pages[0].save(
        "buttons.pdf",
        save_all=True,
        append_images=pdf_pages[1:],
        resolution=pdf_dpi,
    )


if __name__ == "__main__":
    main()
