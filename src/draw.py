from PIL import Image, ImageColor, ImageDraw

Color = int | tuple[int, int, int] | tuple[int, int, int, int]


def _fuzzy_ellipse(
    mode: str,
    size: tuple[int, int],
    foreground: Color,
    background: Color,
) -> Image.Image:
    # draw an ellipse 4x larger than size
    bigsize = (4 * size[0], 4 * size[1])
    ellipse = Image.new(mode, bigsize, background)
    ImageDraw.Draw(ellipse).ellipse((0, 0) + bigsize, fill=foreground)

    # downscale it with antialiasing to get a fuzzy edge
    return ellipse.resize(size, Image.LANCZOS)


def background_ellipse(size: tuple[int, int], color: str) -> Image.Image:
    return _fuzzy_ellipse("RGBA", size, ImageColor.getrgb(color), (0,) * 4)


def ellipse_mask(size: tuple[int, int]) -> Image.Image:
    return _fuzzy_ellipse("L", size, 255, 0)
