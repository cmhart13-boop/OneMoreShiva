"""Prepare the approved One More Shiva trophy for the startup splash.

The source JPEG remains unchanged. This module crops away the portrait canvas and emits
one cached transparent PNG so the browser displays the trophy at useful native detail.
"""
from __future__ import annotations

import base64
import io
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

APPROVED_SPLASH_ASSET = "1FB42328-2FEA-43AE-9BAC-D6BE96E58C93.jpeg"
MIN_RENDER_WIDTH = 720


def _background_color(image: Image.Image) -> tuple[int, int, int]:
    pixels = image.load()
    width, height = image.size
    corners = (
        pixels[0, 0],
        pixels[width - 1, 0],
        pixels[0, height - 1],
        pixels[width - 1, height - 1],
    )
    return tuple(round(sum(pixel[channel] for pixel in corners) / 4) for channel in range(3))


def _crop_to_trophy(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, _background_color(rgb))
    difference = ImageChops.difference(rgb, background).convert("L").filter(ImageFilter.MedianFilter(3))

    alpha = difference.point(
        lambda value: 0
        if value <= 10
        else 255
        if value >= 40
        else round((value - 10) * 255 / 30)
    )
    bbox = alpha.point(lambda value: 255 if value >= 32 else 0).getbbox()
    if bbox is None:
        raise RuntimeError("Approved Shiva splash asset contains no detectable trophy")

    left, top, right, bottom = bbox
    pad = 10
    crop_box = (
        max(0, left - pad),
        max(0, top - pad),
        min(rgb.width, right + pad),
        min(rgb.height, bottom + pad),
    )
    trophy = rgb.crop(crop_box).convert("RGBA")
    trophy.putalpha(alpha.crop(crop_box))

    # An iPhone renders a ~225 CSS-pixel logo at up to 3x density. Prepare one 720px
    # asset once on the server rather than making Safari enlarge a small JPEG every load.
    if trophy.width < MIN_RENDER_WIDTH:
        scale = MIN_RENDER_WIDTH / trophy.width
        target = (MIN_RENDER_WIDTH, max(1, round(trophy.height * scale)))
        trophy = trophy.resize(target, Image.Resampling.LANCZOS)
        trophy = trophy.filter(ImageFilter.UnsharpMask(radius=0.7, percent=105, threshold=3))

    return trophy


@lru_cache(maxsize=1)
def splash_data_uri() -> str:
    source = Path(__file__).with_name(APPROVED_SPLASH_ASSET)
    try:
        with Image.open(source) as image:
            trophy = _crop_to_trophy(image)
        output = io.BytesIO()
        trophy.save(output, format="PNG", optimize=True)
    except Exception as exc:
        raise RuntimeError("Unable to prepare the approved Shiva splash trophy") from exc

    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
