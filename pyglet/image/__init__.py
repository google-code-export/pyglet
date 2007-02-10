#!/usr/bin/env python

'''
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import sys
import re
import warnings

from ctypes import *
from math import ceil
from StringIO import StringIO

from pyglet.gl import *
from pyglet.gl.gl_info import *
from pyglet.image.codecs import *

class ImageException(Exception):
    pass

def load_image(filename, file=None, decoder=None):
    '''Load an image from a file.

    `filename` is used to guess the image format.  

    `file` is a an optional file-like object.  If unspecified, the `filename`
    is opened.
        
    `decoder` is optional and specifies an instance of ImageDecoder.  If
    `decoder` is unspecified, all decoders that are registered for the
    filename extension are tried.  If none succeed, the exception from the
    first decoder is raised.

    Returns an instance of AbstractImage (you can make no assumptions about
    the particular subclass; this depends on the decoder).
    '''

    if not file:
        file = open(filename, 'rb')
    if not hasattr(file, 'seek'):
        file = StringIO(file.read())

    if decoder:
        return decoder.decode(file, filename)
    else:
        first_exception = None
        for decoder in get_decoders(filename):
            try:
                image = decoder.decode(file, filename)
                return image
            except ImageDecodeException, e:
                first_exception = first_exception or e
                file.seek(0)

        if not first_exception:
            raise ImageDecodeException('No image decoders are available')
        raise first_exception 

def create_image(width, height, pattern=None):
    '''Create an image filled with the given pattern.

    If no pattern is specified, the image is completely transparent.
    Otherwise, `pattern` is an instance of ImagePattern.

    Returns an instance of AbstractImage (you can make no assumptions about
    the particular subclass; this depends on the pattern).
    '''
    if not pattern:
        pattern = SolidColorImagePattern()
    return pattern.create_image(width, height)

class ImagePattern(object):
    def create_image(width, height):
        raise NotImplementedError('abstract')

class SolidColorImagePattern(ImagePattern):
    '''Creates an image filled with a solid color.'''

    def __init__(self, color=(0, 0, 0, 0)):
        '''Initialise with the given color.

        'color' must be a 4-tuple of ints in range [0,255].
        '''
        self.color = '%c%c%c%c' % color

    def create_image(width, height):
        data = self.color * width * height
        return ImageData(width, height, 'RGBA', data)

class CheckerImagePattern(ImagePattern):
    '''Creates an image with the pattern::

        1122
        2211

    Where "1" is color1 and "2" is color2.  When tiled, the pattern creates
    a checkerboard appearance.
    ''' 

    def __init__(self, color1=(150,150,150,255), color2=(200,200,200,255))
        '''Initialise with the given colors.

        'color1' and 'color2' must be 4-tuples of ints in range [0,255].
        '''
        self.color1 = '%c%c%c%c' % color1
        self.color2 = '%c%c%c%c' % color2

    def create_image(width, height):
        hw = size/2
        row1 = self.color1 * hw + color2 * hw
        row2 = self.color2 * hw + self.colour1 * hw
        data = row1 * height + row2 * height
        return ImageData(width, height, 'RGBA', data)

class AbstractImage(object):
    '''Abstract class representing an image.
    '''

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_image_data(self):
        '''Retrieve an ImageData instance for this image.'''
        raise ImageException('Cannot retrieve image data for %r' % self)

    image_data = property(get_image_data)

    def get_texture(self):
        '''Retrieve a Texture instance for this image.'''
        raise ImageException('Cannot retrieve texture for %r' % self)

    texture = property(get_texture)

    def get_tileable_texture(self):
        '''Retrieve a TileableTexture instance for this image.'''
        raise ImageException('Cannot retrieve tileable texture for %r' % self)

    tileable_texture = property(get_tileable_texture)

    def save(self, filename=None, file=None, encoder=None):
        '''Save this image to a file.

        If `filename` specified, the extension is used as a hint to the
        encoder for the format to write.

        If `file` is specified, it is a file-like object that is written
        to.  If unspecified, `filename` is opened.

        `encoder` optionally gives an ImageEncoder to use, otherwise all
        encoders matching the filename extension are tried.  If all fail,
        the exception from the first one attempted is raised.
        '''
        if not file:
            file = open(filename, 'wb')

        if encoder:
            encoder.encode(self, file, filename)
        else:
            first_exception = None
            for encoder in get_encoders(filename):
                try:
                    encoder.encode(self, file, filename, options)
                    return
                except ImageDecodeException, e:
                    first_exception = first_exception or e
                    file.seek(0)

            if not first_exception:
                raise ImageEncodeException('No image encoders are available')
            raise first_exception

    def blit(self, source, x, y, z):
        '''Draw `source` on this image.'''
        raise ImageException('Cannot blit images onto %r.' % self)

    def blit_to_texture(self, target, x, y, depth=0):
        '''Draw this image on the currently bound texture at `target`.'''
        raise ImageException('Cannot blit %r to a texture.' % self)

    def blit_to_buffer(self, x, y, z):
        '''Draw this image to the currently enabled buffers.'''
        raise ImageException('Cannot blit %r to a framebuffer.' % self)

class ImageData(AbstractImage):
    '''An image represented as a string or array of unsigned bytes.
    '''

    _swap1_pattern = re.compile('(.)', re.DOTALL)
    _swap2_pattern = re.compile('(.)(.)', re.DOTALL)
    _swap3_pattern = re.compile('(.)(.)(.)', re.DOTALL)
    _swap4_pattern = re.compile('(.)(.)(.)(.)', re.DOTALL)

    def __init__(self, width, height, format, data, pitch=None):
        '''Initialise image data.

        width, height
            Width and height of the image, in pixels
        data
            String or array/list of bytes giving the decoded data.
        format
            A valid format string, such as 'RGB', 'RGBA', 'ARGB', etc.
        pitch
            If specified, the number of bytes per row.  Negative values
            indicate a top-to-bottom arrangement.  
            Defaults to width * len(format).

        '''
        super(ImageData, self).__init__(width, height)

        self._current_format = self._desired_format = format
        self._current_data = data
        if not pitch:
            pitch = width * len(format)
        self._current_pitch = self.pitch = pitch
        self.image_data = self
        self._current_texture = None

    image_data = property(lambda self: self)

    def set_format(self, format):
        self._desired_format = format
        self._current_texture = None

    format = property(lambda self: self._desired_format, set_format)

    def get_data(self):
        if self._current_pitch != self.pitch or \
           self._current_format != self.format:
            self._current_data = self._convert(self.format, self.pitch)
            self._current_format = self.format
            self._current_pitch = self.pitch

        return self._current_data

    def set_data(self, data):
        self._current_data = data
        self._current_format = self.format
        self._current_pitch = self.pitch
        self._current_texture = None

    data = property(get_data, set_data)

    def get_texture(self):
        if self._current_texture:
            return self._current_texture

        texture = Texture.create_for_size(
            GL_TEXTURE_2D, self.width, self.height)
        subimage = False
        if texture.width != self.width or texture.height != self.height:
            texture = texture.get_region(0, 0, self.width, self.height)
            subimage = True

        internalformat = self._get_internalformat(self.format)

        glBindTexture(GL_TEXTURE_2D, texture.id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        if subimage:
            width = texture.owner.width
            height = texture.owner.height
            blank = (c_ubyte * (width * height * 4))()
            glTexImage2D(GL_TEXTURE_2D,
                         0,
                         internalformat,
                         width, height,
                         0,
                         GL_RGBA, GL_UNSIGNED_BYTE,
                         blank) 
            internalformat = None

        self.blit_to_texture(GL_TEXTURE_2D, 0, 0, 0, internalformat)
        
        self._current_texture = texture
        return texture

    texture = get_texture

    def blit_to_buffer(self, x, y, z):
        self.texture.blit_to_buffer(x, y, z)
        
    def blit_to_texture(self, target, x, y, depth, internalformat=None):
        '''Draw this image to to the currently bound texture at `target`.
        If `internalformat` is specified, glTexImage is used to initialise
        the texture; otherwise, glTexSubImage is used to update a region.
        '''

        data_format = self.format
        data_pitch = abs(self._current_pitch)

        # Determine pixel format from format string
        format, type = self._get_gl_format_and_type(data_format)
        if format is None:
            # Need to convert data to a standard form
            data_format = {
                1: 'L',
                2: 'LA',
                3: 'RGB',
                4: 'RGBA'}.get(len(data_format))
            format, type = self._get_gl_format_and_type(data_format)

        # Get data in required format (hopefully will be the same format it's
        # already in, unless that's an obscure format, upside-down or the
        # driver is old).
        data = self._convert(data_format, data_pitch)

        if data_pitch & 0x1:
            alignment = 1
        elif data_pitch & 0x2:
            alignment = 2
        else:
            alignment = 4
        row_length = data_pitch / len(data_format)
        glPushClientAttrib(GL_CLIENT_PIXEL_STORE_BIT)
        glPixelStorei(GL_UNPACK_ALIGNMENT, alignment)
        glPixelStorei(GL_UNPACK_ROW_LENGTH, row_length)

        if internalformat:
            glTexImage2D(GL_TEXTURE_2D,
                         0,
                         internalformat,
                         self.width, self.height,
                         0,
                         format, type,
                         data)
        else:
            glTexSubImage2D(GL_TEXTURE_2D,
                            0,
                            x, y,
                            self.width, self.height,
                            format, type,
                            data)
        glPopClientAttrib()

    def crop(self, x, y, width, height):
        self._ensure_string_data()

        x1 = len(self._current_format) * x
        x2 = len(self._current_format) * (x + width)

        data = self._convert(self._current_format, abs(self._current_pitch))
        rows = re.findall('.' * abs(self._current_pitch), data, re.DOTALL)
        rows = [row[x1:x2] for row in rows[y:y+height]]
        self._current_data = ''.join(rows)
        self._current_pitch = width * len(self._current_format)
        self._current_texture = None

    def _convert(self, format, pitch):
        '''Return data in the desired format; does not alter this instance's
        current format or pitch.
        '''

        if format == self._current_format and pitch == self._current_pitch:
            return self._current_data

        self._ensure_string_data()
        data = self._current_data

        if pitch != self._current_pitch:
            diff = abs(self._current_pitch) - abs(pitch)
            if diff > 0:
                # New pitch is shorter than old pitch, chop bytes off each row
                pattern = re.compile(
                    '(%s)%s' % ('.' * abs(pitch), '.' * diff), re.DOTALL)
                data = pattern.sub(r'\1', data)    
            elif diff < 0:
                # New pitch is longer than old pitch, add '0' bytes to each row
                pattern = re.compile(
                    '(%s)' % '.' * abs(self._current_pitch), re.DOTALL)
                pad = '.' * -diff
                data = pattern.sub(r'\1%s' % pad, data)

            if self._current_pitch * pitch < 0:
                # Pitch differs in sign, swap row order
                rows = re.findall('.' * abs(pitch), data, re.DOTALL)
                rows.reverse()
                data = ''.join(rows)

        if format != self._current_format:
            # Create replacement string, e.g. r'\4\1\2\3' to convert RGBA to
            # ARGB
            repl = ''
            for c in format:
                try:
                    idx = self._current_format.index(c) + 1
                except ValueError:
                    idx = 1
                repl += r'\%d' % idx

            if len(self._current_format) == 1:
                swap_pattern = self._swap1_pattern
            elif len(self._current_format) == 2:
                swap_pattern = self._swap2_pattern
            elif len(self._current_format) == 3:
                swap_pattern = self._swap3_pattern
            elif len(self._current_format) == 4:
                swap_pattern = self._swap4_pattern
            else:
                raise ImageException(
                    'Current image format is wider than 32 bits.')

            packed_pitch = self.width * len(self._current_format)
            if abs(pitch) != packed_pitch:
                # Pitch is wider than pixel data, need to go row-by-row.
                rows = re.findall('.' * abs(pitch), data, re.DOTALL)
                rows = [swap_pattern.sub(repl, r) for r in rows]
                data = ''.join(rows)
            else:
                # Rows are tightly packed, apply regex over whole image.
                data = swap_pattern.sub(repl, data)

        return data

    def _ensure_string_data(self):
        if type(self._current_data) is not str:
            buf = create_string_buffer(len(self._current_data))
            memmove(buf, self.data, len(self._current_data))
            self._current_data = buf.raw

    def _get_gl_format_and_type(self, format):
        if format == 'I':
            return GL_LUMINANCE, GL_UNSIGNED_BYTE
        elif format == 'L':
            return GL_LUMINANCE, GL_UNSIGNED_BYTE
        elif format == 'LA':
            return GL_LUMINANCE_ALPHA, GL_UNSIGNED_BYTE
        elif format == 'RGB':
            return GL_RGB, GL_UNSIGNED_BYTE
        elif format == 'RGBA':
            return GL_RGBA, GL_UNSIGNED_BYTE
        elif format == 'ARGB':
            if (GL_UNSIGNED_BYTE == GL_UNSIGNED_BYTE and
                gl_info.have_extension('GL_EXT_bgra') and
                gl_info.have_extension('GL_APPLE_packed_pixel')):
                return GL_BGRA, GL_UNSIGNED_INT_8_8_8_8_REV
        elif format == 'ABGR':
            if gl_info.have_extension('GL_EXT_abgr'):
                return GL_ABGR_EXT, GL_UNSIGNED_BYTE
        elif format == 'BGR':
            if gl_info.have_extension('GL_EXT_bgra'):
                return GL_BGR, GL_UNSIGNED_BYTE

        return None, None

    def _get_internalformat(self, format):
        if len(format) == 4:
            return GL_RGBA
        elif len(format) == 3:
            return GL_RGB
        elif len(format) == 2:
            return GL_LUMINANCE
        elif format == 'A':
            return GL_ALPHA
        elif format == 'L':
            return GL_LUMINANCE
        elif format == 'I':
            return GL_INTENSITY
        return GL_RGBA

def _nearest_pow2(v):
    # From http://graphics.stanford.edu/~seander/bithacks.html#RoundUpPowerOf2
    # Credit: Sean Anderson
    v -= 1
    v |= v >> 1
    v |= v >> 2
    v |= v >> 4
    v |= v >> 8
    v |= v >> 16
    return v + 1

class Texture(AbstractImage):
    '''An image loaded into video memory that can be efficiently drawn
    to the framebuffer.

    Typically you will get an instance of Texture by accessing the `texture`
    member of any other AbstractImage.
    '''

    tex_coords = ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0))

    def __init__(self, width, height, target, id):
        super(Texture, self).__init__(width, height)
        self.target = target
        self.id = id

    def __del__(self):
        id = GLuint(self.id)
        glDeleteTextures(1, byref(id))

    @classmethod
    def create_for_size(cls, target, min_width, min_height):
        '''Create a Texture with dimensions at least min_width, min_height.

        Many older drivers require that each dimension is a power of 2;
        this constructor ensures that the smallest powers of 2 above the
        minimum dimensions specified are used.
        '''
        if target not in (GL_TEXTURE_RECTANGLE_EXT, GL_TEXTURE_RECTANGLE_ARB):
            width = _nearest_pow2(min_width)
            height = _nearest_pow2(min_height)
        id = GLuint()
        glGenTextures(1, byref(id))
        return cls(width, height, target, id.value)

    def get_image_data(self):
        glBindTexture(self.target, self.id)

        # Determine a suitable format string (could also use internalformat,
        # but this is easier).
        def param(p):
            value = GLint()
            glGetTexLevelParameteriv(self.target, 0, p, byref(value))
            return value.value
        format = ''
        if param(GL_TEXTURE_RED_SIZE):
            format += 'R'
        if param(GL_TEXTURE_GREEN_SIZE):
            format += 'G'
        if param(GL_TEXTURE_BLUE_SIZE):
            format += 'B'
        if param(GL_TEXTURE_LUMINANCE_SIZE):
            format += 'L'
        if param(GL_TEXTURE_INTENSITY_SIZE):
            format += 'I'
        if param(GL_TEXTURE_ALPHA_SIZE):
            format += 'A'

        # Determine GL format for extraction.
        gl_format = {
            'R': GL_RED,
            'G': GL_BLUE,
            'B': GL_GREEN,
            'A': GL_ALPHA,
            'RGB': GL_RGB,
            'RGBA': GL_RGBA,
            'L': GL_LUMINANCE,
            'LA': GL_LUMINANCE_ALPHA,
            'I': GL_LUMINANCE
        }.get(format, None)
        if not gl_format:
            raise ImageException('Invalid texture format "%s"' % format)

        buffer = (GLubyte * (width * height * len(format)))()
        glGetTexImage(GL_TEXTURE_2D, 0, gl_format, GL_UNSIGNED_BYTE, buffer)

        return ImageData(width, height, format, buffer)

    image_data = property(get_image_data)

    texture = property(lambda self: self)

    def blit(self, source, x, y, z):
        glBindTexture(self.target, self.id)
        source.blit_to_texture(x, y, z)

    # no implementation of blit_to_texture yet (could use aux buffer)

    def blit_to_buffer(self, x, y, z):
        # Create interleaved array in T4F_V4F format
        t = self.tex_coords
        w, h = self.width, self.height
        array = (GLfloat * 32)(
             t[0][0], t[0][1], t[0][2], 1.,
             x,       y,       z,       1.,
             t[1][0], t[1][1], t[1][2], 1., 
             x + w,   y,       z,       1.,
             t[2][0], t[2][1], t[2][2], 1., 
             x + w,   y + h,   z,       1.,
             t[3][0], t[3][1], t[3][2], 1., 
             x,       y + h,   z,       1.)

        glPushAttribs(GL_ENABLE_BIT)
        glEnable(self.target)
        glBindTexture(self.target, self.id)
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glInterleavedArrays(GL_T4F_V4F, 0, array)
        glDrawArrays(GL_QUADS, 0, 4)
        glPopClientAttrib()
        glPopAttrib()

    def get_region(self, x, y, width, height):
        u1 = x / float(self.width)
        v1 = y / float(self.height)
        u2 = (x + width) / float(self.width)
        v2 = (y + height) / float(self.height)
        z1 = self.tex_coords[0][2]
        z2 = self.tex_coords[1][2]
        z3 = self.tex_coords[2][2]
        z4 = self.tex_coords[3][2]
        return TextureRegion(width, height, self,
            ((u1, v1, z1), (u2, v1, z2), (u2, v2, z3), (u1, v2, z4)))


class TextureRegion(Texture):
    '''A rectangular region of a texture, presented as if it were
    a separate texture.
    '''

    def __init__(self, width, height, owner, tex_coords):
        super(TextureRegion, self).__init__(
            width, height, owner.target, owner.id)
        
        self.owner = owner
        self.tex_coords = tex_coords

    def get_image_data(self):
        me_x = self.tex_coords[0][0] * self.owner.width
        me_y = self.tex_coords[0][1] * self.owner.height
        image_data = super(TextureRegion, self).get_image_data()
        image_data.crop(me_x, me_y, self.width, self.height)
        return image_data

    def get_region(self, x, y, width, height):
        me_x = self.tex_coords[0][0] * self.owner.width
        me_y = self.tex_coords[0][1] * self.owner.height
        region = super(TextureRegion, self).get_region(
            me_x + x, me_y + y, width, height)
        region.owner = self.owner
        return region

class BufferImage(AbstractImage):
    def __init__(self, gl_format=GL_RGBA, buffer=GL_BACK, 
                 x=None, y=None, width=None, height=None):
        self.gl_format = gl_format
        self.buffer = buffer
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_raw_image(self, type=GL_UNSIGNED_BYTE):
        x = self.x
        y = self.y
        width = self.width
        height = self.height
        viewport = (c_int * 4)()
        glGetIntegerv(GL_VIEWPORT, viewport)
        if x is None:
            x = viewport[0]
        if y is None:
            y = viewport[1]
        if width is None:
            width = viewport[2]
        if height is None:
            height = viewport[3]


        gl_formats = {
            GL_STENCIL_INDEX: 'L',
            GL_DEPTH_COMPONENT: 'L',
            GL_RED: 'L',
            GL_GREEN: 'L',
            GL_BLUE: 'L',
            GL_ALPHA: 'A',
            GL_RGB: 'RGB',
            GL_BGR: 'BGR',
            GL_RGBA: 'RGBA',
            GL_BGRA: 'BGRA',
            GL_LUMINANCE: 'L',
            GL_LUMINANCE_ALPHA: 'LA',
        }
        format = gl_formats[self.gl_format]
        pixels = (self.get_type_ctype(type) * (len(format) * width * height))()

        glReadBuffer(self.buffer)
        glReadPixels(x, y, width, height, self.gl_format, type, pixels)

        return RawImage(pixels, width, height, format, type)

    def texture(self, internalformat=None):
        raise NotImplementedError('TODO')

    def texture_subimage(self, x, y):
        raise NotImplementedError('TODO')

class StencilImage(BufferImage):
    def __init__(self, x=None, y=None, width=None, height=None):
        super(StencilImage, self).__init__(GL_STENCIL_INDEX, GL_BACK,
            x, y, width, height)

class DepthImage(BufferImage):
    def __init__(self, x=None, y=None, width=None, height=None):
        super(DepthImage, self).__init__(GL_DEPTH_COMPONENT, GL_BACK,
            x, y, width, height)

class AllocatingTextureAtlasOutOfSpaceException(ImageException):
    pass

class AllocatingTextureAtlas(Texture):
    x = 0
    y = 0
    line_height = 0
    subimage_class = TextureSubImage

    def allocate(self, width, height):
        '''Returns (x, y) position for a new glyph, and reserves that
        space.'''
        if self.x + width > self.width:
            self.x = 0
            self.y += self.line_height
            self.line_height = 0
        if self.y + height > self.height:
            raise AllocatingTextureAtlasOutOfSpaceException()

        self.line_height = max(self.line_height, height)
        x = self.x
        self.x += width
        return self.subimage_class(self, x, self.y, width, height)


# Initialise default codecs
add_default_image_codecs()


"""
# code to stretch texture
    def stretch(self):
        '''Make this image stretch to fill its entire texture dimensions,
        leaving no border.
        
        The width, height of the texture are unchanged. Required for tiling
        non-power-2 images.

        If the power-2 size of the texture is larger than the window size,
        part of the texture may be lost as OpenGL silently restricts the
        viewport size.  If this is a problem, avoid this function and create
        your images of power-2 size to start with.
        '''
        tex_width, tex_height, u, v = \
            Texture.get_texture_size(self.width, self.height)
        if tex_width == self.width and tex_height == self.height:
            return

        # Interleaved array for quad filling normalized device coords.
            # u v     x y z
        ar = [0, 0,   -1, -1, 0,
              u, 0,    1, -1, 0,
              u, v,    1,  1, 0,
              0, v,   -1,  1, 0]
        ar = (c_float * len(ar))(*ar)

        #buffer = allocate_aux_buffer()
        aux_buffers = c_int()
        glGetIntegerv(GL_AUX_BUFFERS, byref(aux_buffers))
        if aux_buffers.value < 1:
            warnings.warn('No aux buffer available.  Request one in window \
                creation to avoid destroying the color buffer during \
                texture operations.')
            buffer = GL_BACK
        else:
            buffer = GL_AUX0

        alpha_bits = c_int()
        glGetIntegerv(GL_ALPHA_BITS, byref(alpha_bits))
        if alpha_bits.value == 0:
            warnings.warn('No alpha channel in color/aux buffer.  Request \
                alpha_size=8 in window creation to avoid losing the alpha \
                channel of textures during texture operations.')

        glDrawBuffer(buffer)

        old_clear_color = (c_float * 4)()
        glGetFloatv(GL_COLOR_CLEAR_VALUE, old_clear_color)
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        old_viewport = (c_int * 4)()
        glGetIntegerv(GL_VIEWPORT, old_viewport)
        glViewport(0, 0, tex_width, tex_height)
        glBindTexture(GL_TEXTURE_2D, self.id)

        # Ya know, this would be indented properly if it wasn't Python ;-)
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glPushAttrib(GL_CURRENT_BIT | GL_ENABLE_BIT)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glColor3f(1, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glInterleavedArrays(GL_T2F_V3F, 0, ar)
        glDrawArrays(GL_QUADS, 0, 4)
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopAttrib()
        glPopClientAttrib()

        glReadBuffer(buffer)
        glCopyTexSubImage2D(GL_TEXTURE_2D,
            0,
            0, 0,
            0, 0,
            tex_width, tex_height)

        glViewport(*old_viewport)
        glClearColor(*old_clear_color)
        self.uv = (1.,1.)

        glDrawBuffer(GL_BACK)

"""
