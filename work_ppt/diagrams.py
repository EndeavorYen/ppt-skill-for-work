from __future__ import annotations

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.oxml.ns import nsmap
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

NAVY = RGBColor(0x00, 0x44, 0x79)
INK = RGBColor(0x11, 0x11, 0x11)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


def _box(slide, x, y, w, h, text, fill=NAVY, font_color=WHITE, size=12):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.color.rgb = font_color
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    return shape


def _arrow(slide, x1, y1, x2, y2):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    conn.line.color.rgb = INK
    conn.line.width = Pt(1.5)
    return conn


def add_process_row(slide, labels: list[str], top=Inches(2.1)) -> None:
    n = len(labels)
    if n == 0:
        return
    margin = Inches(0.5)
    gap = Inches(0.25)
    width = Inches(12.3)
    box_w = int((width - gap * (n - 1)) / n)
    box_h = Inches(1.05)
    x = margin
    boxes = []
    for label in labels:
        boxes.append(_box(slide, x, top, box_w, box_h, label, size=11))
        x += box_w + gap
    for a, b in zip(boxes, boxes[1:]):
        _arrow(
            slide,
            a.left + a.width,
            a.top + a.height // 2,
            b.left,
            b.top + b.height // 2,
        )


def add_architecture_stack(slide, layers: list[str], left=Inches(1.2), top=Inches(1.8)) -> None:
    w = Inches(10.5)
    h = Inches(0.85)
    gap = Inches(0.18)
    fills = [RGBColor(0x00, 0x44, 0x79), RGBColor(0x00, 0x05, 0x42), RGBColor(0x5E, 0x5E, 0x5E), NAVY]
    y = top
    for i, layer in enumerate(layers):
        _box(slide, left, y, w, h, layer, fill=fills[i % len(fills)], size=14)
        y += h + gap
