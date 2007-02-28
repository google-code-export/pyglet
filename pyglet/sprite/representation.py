from pyglet.sprite.geometry import *
from pyglet.gl import *

class SpriteRepresentation:
    def draw(self, sprite):
         # Draw the given body at its position/orientation/time.
         raise NotImplementedError('Implement in subclass')
 
    def draw_many(self, sprite):
        # Draw a list of bodies at their positions/orientations/times.
        # Default implementation is:
        for sprite in sprites:
            self.draw(sprite)
 
class ImageSpriteRepresentation(SpriteRepresentation):
    '''
    '''
    # XXX draw and draw_many assert isinstance(sprite, ImageSprite)

    cache = {}

    def __new__(cls, texture, origin):
        if (texture, origin) in self.cache:
            return self.cache[texture, origin]
        o = self.cache[texture, origin] = cls(texture, origin)
        return o

    def __init__(self, texture, origin=(0,0)):
        self.texture = texture
        self.origin = origin

        t = texture.tex_coords
        w, h = texture.width, texture.height
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        # using vertex arrays is slower :(
        glBegin(GL_QUADS)
        glTexCoord3f(*t[0])
        glVertex2f(0, 0)
        glTexCoord3f(*t[1])
        glVertex2f(w, 0)
        glTexCoord3f(*t[2])
        glVertex2f(w, h)
        glTexCoord3f(*t[3])
        glVertex2f(0, h)
        glEnd()
        glEndList()

    def key(self):
        return ('ImageSpriteRepresentation', self.texture.id, self.origin)

    def draw(self, sprite):
        glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.texture.blit(sprite.x, sprite.y, 0)
        glPopAttrib()
 
    # draw_many can be optimised by binding texture / state once.
    def draw_many(self, sprites):
        glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(self.texture.target)
        glBindTexture(self.texture.target, self.texture.id)

        ox = oy = 0
        for sprite in sprites:
            dx, dy = self.origin
            x, y = sprite.x - dx, sprite.y - dy
            # XXX self.origin
            glTranslatef(x-ox, y-oy, 0)
            glCallList(self.display_list)
            ox, oy = x, y

        glPopAttrib()

    def geometry_factory(self, sprite):
        # XXX sprite.orientation
        dx, dy = self.origin
        w, h = self.texture.width, self.texture.height
        return RectGeometry(sprite, sprite.x-dx, sprite.y-dy, w, h)
 
class AnimatedImageSpriteRepresentation(SpriteRepresentation):
    # or Texture, in which case this behaves same as ImageSpriteRepresentation
    '''
    texture = UniformTextureSequence()
    timings = ...  (map time to sequence number: float or list or function?)
    '''
 
    # draw_many can be optimised by binding texture / state once.
    # draw and draw_many assert isinstance(sprite, AnimatedImageSprite)
 
class OwnerDrawSpriteRepresentation(SpriteRepresentation):
    # good for easy subclassing of Sprite.. no need to write a separate
    # representation class.  (but, no optimisation happens)
 
    # draw asserts isinstance(sprite, OwnerDrawSprite)
    # draw() calls sprite.draw().
    pass
 
# XXX name too similar to SpriteGeometry, but no relation.
class GeometrySpriteRepresentation(SpriteRepresentation):
    # draws a euclid geometry object (rectangle, circle, ellipse, ..)
    pass
 
class TextSpriteRepresentation(SpriteRepresentation):
    # self explanatory
    pass
 
class SpriteGroupRepresentation(SpriteRepresentation):
    # can only be attached to SpriteGroup.
 
    # draw asserts isinstance(sprite, SpriteGroup)
    # draw() applies transform in Sprite (and temporarily adds time to
    # children), then calls child.representation.draw(child) for each child.
    pass

