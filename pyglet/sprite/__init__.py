'''
'''

from pyglet.euclid import *
from pyglet.image import ImageData

from pyglet.sprite.camera import *
from pyglet.sprite.view import *
from pyglet.sprite.map import *
from pyglet.sprite.representation import *

class Sprite(object):
    '''A 2d object oriented and positioned in space-time.

    :Parameters:
        `position` : Point2()
            Positions the Sprite in space. The representation and collider
            are based off this point with their own optional origins.
        `representation` : SpriteRepresentation()
            Visual representation of the sprite, could be an image, some
            drawn geometry or even a call back to a .draw() method on a
            Sprite subclass.
        `collider` : SpriteCollider()
            Defines how the sprite collides with other sprites. [XXX By
            default the sprite geometry is copied.]
        `orientation` : float()
            Degrees counter-clockwise  (can be 0 on class). Rotates the
            sprite about the origins of the representation and collider.
        `time` : float()
            Used for timing animations and movement, in seconds. Defaults
            to 0 on Sprite initialisation [XXX and automatically
            incremented]
 
    :Optional Parameters:
        `blueprint` : dict()
            Values from XML file shared amongst similar Sprites.
 
        TODO: scheduling
        `velocity` : property(...) # schedules an update for position
        `acceleration` : property(...)     # schedules an update for velocity
        `angular_velocity` : property(...) # schedules an update for orientation
        `dx, dy, ddx, ddy                 # synonyms for velocity/acceleration
    '''
    def __init__(self, representation, position=(0,0), orientation=0,
            collider=None, time=0, blueprint=None, velocity=(0,0),
            acceleration=(0,0), angular_velocity=0):

        self.representation = representation
        self.collider = collider
        self.blueprint = blueprint is not None or {}

        self.time = time
        self.orientation = orientation
        self.x, self.y = position
        self.dx, self.dy = velocity
        self.ddx, self.ddy = acceleration
        self.angular_velocity = angular_velocity
 
    def get_position(self):
        return Point2(self.x, self.y)
    def set_position(self, position):
        self.x, self.y = position
    position = property(get_position, set_position)
 
    def get_velocity(self):
        return Vector2(self.dx, self.dy)
    def set_velocity(self, velocity):
        self.dx, self.dy = velocity
    velocity = property(get_velocity, set_velocity)
 
    def get_acceleration(self):
        return Vector2(self.ddx, self.ddy)
    def set_acceleration(self, acceleration):
        self.ddx, self.ddy = acceleration
    acceleration = property(get_acceleration, set_acceleration)

    def geometry_factory(self, sprite):
        return self.representation.geometry_factory(sprite)
    def get_geometry(self):
        return self.geometry_factory(self)
    geometry = property(get_geometry)
 
    def x__getattr__(self, name):
        try:
            return self.blueprint[name]
        except KeyError:
            raise AttributeError, name


class ImageSprite(Sprite):
    '''Upon creation sets representation to an ImageSpriteRepresentation

    :Parameters:
        `tint_color` : float 4-tuple
            Ignored if blend_color is not None.
        `blend_color` : float 4-tuple
            4-tuple of floats if not None.

    '''
    def __init__(self, image, position=(0,0), orientation=0,
            collider=None, time=0, blueprint=None, velocity=(0,0),
            acceleration=(0,0), angular_velocity=0, tint_color=(1, 1, 1, 1),
            blend_color=None):
        # XXX hmmm...
        if isinstance(image, ImageSpriteRepresentation):
            representation = image
        elif isinstance(image, ImageData):
            representation = ImageSpriteRepresentation.new(image.texture)
        else:
            # assume Texture interface
            representation = ImageSpriteRepresentation.new(image)
        super(ImageSprite, self).__init__(representation, position, orientation,
            collider, time, blueprint, velocity, acceleration,
            angular_velocity)

        self.tint_color = tint_color
        self.blend_color = blend_color

    def draw(self):
        #assert isinstance(sprite, ImageSprite)
        self.representation.draw(self)
    def draw_many(self, sprites):
        self.representation.draw_many(sprites)


class AnimatedImageSprite(ImageSprite):
    '''Upon creation sets representation to instance of
    AnimatedImageRepresentation and also schedules an update method for
    self.time.

    This class can also seamlessly use a non-animating image, slightly
    less efficiently. Period, loop and timings are ignored if
    self.representation.texture is Texture not TextureSequence.

    :Parameters:
        `loop` : boolean()
            If True, modulo self.time by sequence time.
        `period` : float()
            Default 0.25. Ignored if self.timings is not None,
            otherwise gives seconds btwn frames.
        `timings` : None
            Optional sequence of (index, time), where index is into image
            sequence and time is number of seconds of that image.

    '''
    def __init__(self, image, position=(0,0), orientation=0,
            collider=None, time=0, blueprint=None, velocity=(0,0),
            acceleration=(0,0), angular_velocity=0, tint_color=(1, 1, 1, 1),
            blend_color=None, loop=True, period=0.25, timings=None):

        super(AnimatedImageSprite, self).__init__(image, position,
            orientation, collider, time, blueprint, velocity, acceleration,
            angular_velocity, tint_color, blend_color)

        self.loop = loop
        self.period = period
        self.timings = timings
 

class TextSprite(Sprite):
    '''Upon creation, sets representation to TextSpriteRepresentation
    (can probably keep class mapping on font)
 
    :Parameters:
        `font` : property(...)
        `text` : property(...)
            These two properties update the representation
        `color` : float 4-tuple
            Default (1, 1, 1, 1).
        `horizontal_alignment` : 'left', 'right', 'center'
            Default 'left'
        `vertical_alignment` : 'bottom', 'baseline', 'middle', 'top'
            Default 'baseline'

    :Attributes:
        `width` : int()
            Changing width affects representation (wrapping)
        `height` : int()
            Set automatically whenever font or text changes
    '''
    def __init__(self, font, text, position=(0,0), orientation=0,
            collider=None, time=0, blueprint=None, velocity=(0,0),
            acceleration=(0,0), angular_velocity=0, color=(1, 1, 1, 1),
            horizontal_alignment='left', vertical_alignment='baseline',
            width=None):
        representation = TextSpriteRepresentation(font, text, width)
        if geometry is None:
            geometry = RectSpriteGeometry.from_image(image)
        super(TextSprite, self).__init__(representation, position,
            orientation, collider, time, blueprint, velocity, acceleration,
            angular_velocity)

        self.width = width

        # XXX property
        #self.height = representation.???.height
 

class OwnerDrawSprite(Sprite):
    def draw(self):
        raise NotImplementedError('Implement me')

    def geometry_factory(self):
        raise NotImplementedError('Implement me')
 

class SpriteGroup(Sprite):
    children = []
    #representation = GroupRepresentation()


@register_factory('blueprint')
def blueprint_factory(resource, tag):
    id = tag.getAttribute('id')
    properties = resource.handle_properties(tag)
    resource.add_resource(id, properties)
    return properties

