# math2d_text.py

from math2d_aa_rect import AxisAlignedRectangle
from OpenGL.GLUT import *
from OpenGL.GL import *

class TextRenderer(object):
    def __init__(self, font=None):
        self.font = GLUT_STROKE_ROMAN if font is None else font

    def render_text(self, text, rect):
        total_width = 0.0
        for char in text:
            width = glutStrokeWidth(self.font, ord(char))
            total_width += float(width)
        text_rect = AxisAlignedRectangle()
        text_rect.min_point.x = 0.0
        text_rect.max_point.x = total_width
        text_rect.min_point.y = 0.0
        text_rect.max_point.y = 119.05
        original_height = text_rect.Height()
        text_rect.ExpandToMatchAspectRatioOf(rect)
        height = text_rect.Height()
        scale = rect.Width() / text_rect.Width()
        glPushMatrix()
        try:
            glTranslatef(rect.min_point.x, rect.min_point.y + (height - original_height) * 0.5 * scale, 0.0)
            glScalef(scale, scale, 1.0)
            for char in text:
                glutStrokeCharacter(self.font, ord(char))
        finally:
            glPopMatrix()