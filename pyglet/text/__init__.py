#!/usr/bin/env python

'''

No bidi support needs to be in from the start, but keep in mind it will 
be eventually, so don't make it too left-to-rightist.

'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import sys
import os

from pyglet.GL.VERSION_1_1 import *
from pyglet.image import *

class Glyph(TextureSubImage):
    advance = 0
    vertices = (0, 0, 0, 0)

    def set_bearings(self, baseline, left_side_bearing, advance):
        self.advance = advance
        self.vertices = (
            left_side_bearing,
            -baseline,
            left_side_bearing + self.width,
            -baseline + self.height)

    def draw(self):
        '''Debug method: use the higher level APIs for performance and
        kerning.'''
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_QUADS)
        glTexCoord2f(self.tex_coords[0], self.tex_coords[1])
        glVertex2f(self.vertices[0], self.vertices[1])
        glTexCoord2f(self.tex_coords[2], self.tex_coords[1])
        glVertex2f(self.vertices[2], self.vertices[1])
        glTexCoord2f(self.tex_coords[2], self.tex_coords[3])
        glVertex2f(self.vertices[2], self.vertices[3])
        glTexCoord2f(self.tex_coords[0], self.tex_coords[3])
        glVertex2f(self.vertices[0], self.vertices[3])
        glEnd()

    def get_kerning_pair(self, right_glyph):
        return 0

class GlyphTextureAtlas(AllocatingTextureAtlas):
    subimage_class = Glyph

class StyledText(object):
    '''One contiguous sequence of characters sharing the same
    GL state.'''
    # TODO Not there yet: must be split on texture atlas changes.
    def __init__(self, text, font):
        self.text = text
        self.font = font
        self.glyphs = font.get_glyphs(text)

class TextLayout(object):
    '''Will eventually handle all complex layout, line breaking,
    justification and state sorting/coalescing.'''
    def __init__(self, styled_texts):
        self.styled_texts = styled_texts

    def draw(self):
        glPushAttrib(GL_ENABLE_BIT)
        glEnable(GL_TEXTURE_2D)
        glPushMatrix()
        for styled_text in self.styled_texts:
            styled_text.font.apply_blend_state()
            for glyph in styled_text.glyphs:
                glyph.draw()
                glTranslatef(glyph.advance, 0, 0)
        glPopMatrix()
        glPopAttrib()

class BaseFont(object):
    texture_width = 256
    texture_height = 256

    def __init__(self):
        self.textures = []
        self.glyphs = {}

    @classmethod
    def add_font_data(cls, data):
        # Ignored unless overridden
        pass

    def create_glyph_texture(self):
        texture = GlyphTextureAtlas.create(
            self.texture_width,
            self.texture_height,
            GL_LUMINANCE_ALPHA)
        return texture

    def apply_blend_state(self):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

    def allocate_glyph(self, width, height):
        # Search atlases for a free spot
        for texture in self.textures:
            try:
                return texture.allocate(width, height)
            except AllocatingTextureAtlasOutOfSpaceException:
                pass

        # If requested glyph size is bigger than atlas size, increase
        # next atlas size.  A better heuristic could be applied earlier
        # (say, if width is > 1/4 texture_width).
        if width > self.texture_width or height > self.texture_height:
            self.texture_width, self.texture_height, u, v= \
                Texture.get_texture_size(width * 2, height * 2)

        texture = self.create_glyph_texture()
        self.textures.insert(0, texture)

        # This can't fail.
        return texture.allocate(width, height)

    def get_glyph_renderer(self):
        raise NotImplementedError('Subclass must override')

    def get_glyphs(self, text):
        glyph_renderer = None
        for c in text:
            if c not in self.glyphs:
                if not glyph_renderer:
                    glyph_renderer = self.get_glyph_renderer()
                self.glyphs[c] = glyph_renderer.render(c)
        return [self.glyphs[c] for c in text] 

    def render(self, text):
        return TextLayout([StyledText(text, self)])

class GlyphRenderer(object):
    def render(self, text):
        pass

# Load platform dependent module
if sys.platform == 'darwin':
    from pyglet.text.carbon import CarbonFont
    _font_class = CarbonFont
elif sys.platform == 'win32':
    from pyglet.text.win32 import Win32Font
    _font_class = Win32Font
else:
    from pyglet.text.freetype import FreeTypeFont
    _font_class = FreeTypeFont

class Font(object):
    def __new__(cls, name, size, bold=False, italic=False):
        # TODO: Cache fonts, lookup bitmap fonts.
        return _font_class(name, size, bold=bold, italic=italic)

    @staticmethod
    def add_font(font):
        if type(font) in (str, unicode):
            font = open(font, 'r')
        if hasattr(font, 'read'):
            font = font.read()
        _font_class.add_font_data(font)


    @staticmethod
    def add_font_dir(dir):
        import os
        for file in os.listdir(dir):
            if file[:-4].lower() == '.ttf':
                add_font(file)


