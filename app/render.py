import io
import zlib
from functools import cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ASSETS = Path(__file__).parent / "assets"
SIZE = 1000
DESIGN = 1500

WHITE, BLACK, DARK, GREY = (255, 255, 255), (0, 0, 0), (45, 45, 50), (125, 140, 154)
SHADOW = ((20, 95, 12), (16, 6, 4))  # opacity, blur, y-offset

TME_COLORS = (
    (216, 104, 80), (48, 120, 136), (152, 128, 80), (96, 160, 72), (56, 160, 104), (17, 21, 24),
    (208, 88, 152), (88, 96, 208), (104, 120, 136), (112, 88, 152), (120, 96, 64), (136, 96, 224),
    (48, 136, 232), (152, 72, 72), (184, 96, 216), (192, 152, 56),
)  # fmt: skip


def u(v: float) -> float:
    return v * SIZE / DESIGN


def _folder(tld: str) -> str:
    return tld.replace(".", "")


@cache
def _asset(path: str) -> Image.Image:
    return Image.open(ASSETS / path).convert("RGB")


@cache
def _font(path: str, px: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(ASSETS / path), px)


@cache
def _rules(tld: str) -> tuple[str, ...]:
    """Background filenames are the length rules that select them."""
    return tuple(sorted(p.stem for p in (ASSETS / _folder(tld)).glob("*.webp")))


@cache
def _font_size_for_xheight(xh: float, font: str) -> int:
    _, top, _, bottom = _font(font, 200).getbbox("x")
    return round(u(xh) * 200 / (bottom - top))


def _matches(rule: str, n: int) -> bool:
    if rule in ("2n", "2n+1"):
        return n % 2 == (rule == "2n+1")
    if rule.endswith("+"):
        return n >= int(rule[:-1])
    low, _, high = rule.partition("-")
    return int(low) <= n <= int(high or low)


def _background(tld: str, name: str) -> Image.Image:
    length = max(len(name.split(".")[0].encode()), 1)
    rule = next(r for r in _rules(tld) if _matches(r, length))
    return _asset(f"{_folder(tld)}/{rule}.webp").copy()


def _fit(
    draw: ImageDraw.ImageDraw,
    prefix: str,
    name: str,
    suffix: str,
    font: str,
    px: float,
    max_w: float,
    min_px: float,
) -> tuple[str, int, float]:
    """Shrinks the label until it fits, then elides the middle of the name."""

    def w(text: str, size: int) -> float:
        return draw.textlength(text, _font(font, size))

    label = prefix + name + suffix
    while w(label, round(px)) > max_w and px > min_px:
        px -= u(6)  # fractional, or the shrink drifts from the design at other SIZEs
    size = round(px)
    if w(label, size) <= max_w:
        return label, size, w(label, size)

    for keep in range(len(name) - 1, 0, -1):
        label = prefix + name[: (keep + 1) // 2] + "..." + name[len(name) - keep // 2 :] + suffix
        if w(label, size) <= max_w:
            return label, size, w(label, size)
    label = prefix + "..." + suffix
    return label, size, w(label, size)


def _pill_mask(w: int, h: int, radius: int) -> Image.Image:
    """ImageDraw cannot antialias, hence the 2x pass. Caching by w would never hit."""
    ss = 2
    mask = Image.new("L", (w * ss, h * ss))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius=radius * ss, fill=255)
    return mask.resize((w, h), Image.Resampling.LANCZOS)


def _pill(
    canvas: Image.Image,
    cy: float,
    width: float,
    height: float,
    radius: float,
    fill: tuple,
    shadow: bool = False,
) -> None:
    h, r = round(height), round(radius)
    w = max(round(width), 2 * r)
    x, y = SIZE // 2 - w // 2, round(cy) - h // 2
    mask = _pill_mask(w, h, r)
    for opacity, blur, dy in SHADOW if shadow else ():
        margin = round(3 * u(blur))
        spread = Image.new("L", (w + 2 * margin, h + 2 * margin))
        spread.paste(mask, (margin, margin))
        spread = spread.filter(ImageFilter.GaussianBlur(u(blur))).point(lambda a: a * opacity // 255)
        canvas.paste(BLACK, (x - margin, y - margin + round(u(dy))), spread)
    canvas.paste(fill, (x, y), mask)


def _line(draw: ImageDraw.ImageDraw, cy: float, text: str, font: str, px: int, fill: tuple) -> None:
    """Centers on the x-height, the way the pill is centered — not on the baseline."""
    draw.text((SIZE // 2, cy + px * (1 / 2 - 1 / 4.5)), text, font=_font(font, px), fill=fill, anchor="ms")


def _encode(canvas: Image.Image) -> bytes:
    out = io.BytesIO()
    # method 2 encodes twice as fast as the default 4 for the same bytes; quality above 90
    # only reproduces the dithering in the backgrounds, invisible and 3x the size
    canvas.save(out, "WEBP", quality=90, method=2)
    return out.getvalue()


def _card(
    name: str,
    *,
    tld: str,
    cy: float,
    px: int,
    max_w: float,
    min_px: float,
    pad: float,
    height: float,
    radius: float,
    fill: tuple,
    ink: tuple,
    prefix: str = "",
    suffix: str = "",
    shadow: bool = False,
    lift: float = 0,
) -> bytes:
    canvas = _background(tld, name)
    draw = ImageDraw.Draw(canvas)
    font = f"{_folder(tld)}/font.ttf"
    text, size, width = _fit(draw, prefix, name, suffix, font, u(px), u(max_w), u(min_px))
    _pill(canvas, u(cy - lift), width + u(pad), u(height), u(radius), fill, shadow)
    _line(draw, u(cy), text, font, size, ink)
    return _encode(canvas)


WHITE_CARD = dict(
    px=135, max_w=1148, min_px=59, pad=176, height=337, radius=106,
    fill=WHITE, ink=BLACK, shadow=True, lift=12,
)  # fmt: skip


def render_ton(name: str) -> bytes:
    return _card(name, tld="ton", cy=750, suffix=".ton", **WHITE_CARD)


def render_gg(name: str) -> bytes:
    return _card(name, tld="gg", cy=1053, prefix="@", **WHITE_CARD)


def render_gram(name: str) -> bytes:
    return _card(
        name, tld="gram", cy=750, suffix=".gram",
        px=150, max_w=999, min_px=90, pad=200, height=360, radius=116, fill=DARK, ink=WHITE,
    )  # fmt: skip


def render_tme(name: str) -> bytes:
    """Not a _card: the pill scales with the label and a caption sits below it."""
    canvas = _background("t.me", name)
    draw = ImageDraw.Draw(canvas)
    color = TME_COLORS[zlib.crc32(name.split(".")[0].encode()) % len(TME_COLORS)]

    full = _font_size_for_xheight(80, "tme/font.otf")
    text, size, width = _fit(draw, "@", name, "", "tme/font.otf", full, u(1144), u(88))
    k = size / full
    _pill(canvas, u(1124), width + u(198 * k), u(288 * k), u(68 * k), color)
    draw.text((SIZE // 2, u(1124 + 52 * k)), text, font=_font("tme/font.otf", size), fill=WHITE, anchor="ms")

    cap_px = _font_size_for_xheight(37.5, "tme/caption.otf")
    caption, cap_size, _ = _fit(draw, "", name, ".t.me", "tme/caption.otf", cap_px, u(1320), u(40))
    draw.text((SIZE // 2, u(1408)), caption, font=_font("tme/caption.otf", cap_size), fill=GREY, anchor="ms")
    return _encode(canvas)
