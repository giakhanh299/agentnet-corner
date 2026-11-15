"""TextCard: the title card that carries the hook text.

White card, thick ink border, Be Vietnam Pro Bold title, optional grey
subtitle. The title auto-fits the card width — never overflows the frame.
Text is rendered with Manim Text (Pango). NEVER Tex/LaTeX.
"""

from __future__ import annotations

from pathlib import Path

from manim import RoundedRectangle, Text, VGroup, register_font

from config import FONT_FAMILY, FONT_SIZE_BODY, FONT_SIZE_TITLE, SPEC
from src.utils.text import normalize_text, split_text

INK = SPEC["INK"]
ACCENT = SPEC["ACCENT"]
WHITE = SPEC["WHITE"]
GREY = SPEC["GREY"]
FONTS = Path(__file__).resolve().parents[1] / "assets" / "fonts"


class TextCard(VGroup):
    """A bordered card with a (possibly multi-line) title."""

    def __init__(
        self,
        title: str | list[str],
        subtitle: str | None = None,
        accent: str | None = None,
        max_width: float = 7.4,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if isinstance(title, str):
            lines = split_text(title, max_chars=22)
        else:
            lines = [normalize_text(t) for t in title]
        title_text = "\n".join(lines)
        t2c = {normalize_text(accent): ACCENT} if accent else {}
        with register_font(FONTS / "BeVietnamPro-Bold.ttf"):
            text = Text(
                title_text,
                font=FONT_FAMILY,
                weight="BOLD",
                font_size=FONT_SIZE_TITLE,
                color=INK,
                t2c=t2c,
                line_spacing=1.15,
            )
        inner_w = max_width - 1.0
        if text.width > inner_w:
            text.scale(inner_w / text.width)

        parts: list = [text]
        if subtitle:
            with register_font(FONTS / "BeVietnamPro-Regular.ttf"):
                sub = Text(
                    normalize_text(subtitle),
                    font=FONT_FAMILY,
                    font_size=FONT_SIZE_BODY,
                    color=GREY,
                )
            if sub.width > inner_w:
                sub.scale(inner_w / sub.width)
            sub.next_to(text, direction=(0, -1, 0), buff=0.25)
            parts.append(sub)
        content = VGroup(*parts)

        card = RoundedRectangle(
            corner_radius=0.25,
            width=content.width + 1.0,
            height=content.height + 0.9,
            color=INK,
            stroke_width=6,
        )
        card.set_fill(WHITE, opacity=1)
        content.move_to(card.get_center())
        self.add(card, content)
        self.title = text
