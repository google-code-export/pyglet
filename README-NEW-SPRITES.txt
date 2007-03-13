The following was copied from the pyglet wiki and represents the design at
the point that this branch was abandoned in favour of implementing a
simpler API.






===== Sprite Model =====

  * excuse the long class names
  * position = Point2() means, position is an attribute whose value is an instance of Point2

No "Cell" or "Tile".  A Map is a regular arrangement of Sprites.  A Tile is a SpriteRepresentation.

Top-level sprite class is:

<code python>
class Sprite:
    # An interface for something oriented and positioned in space-time.
    x, y  ->  float(), float()
    position -> property() Point2 over .x, .y
    geometry -> SpriteGeometry
    representation -> SpriteRepresentation
    orientation = float()            # degrees counter-clockwise  (can be 0 on class)
    time = float()                   # seconds  (can be 0 on class)    
    collider -> SpriteCollider

    blueprint = dict()               # values from XML file shared amongst similar Sprites
    __getattr__                      # looks up entries in blueprint

    # Optional - clearly not used for "map sprites"
    dx, dy -> float(), float()         # schedules an update for position
    velocity = property(...)          # property() Vector2 over dx, dy
    ddx, ddy -> float(), float()      # schedules an update for velocity
    acceleration = property(...)    # property() Vector2 over ddx, ddy
    angular_velocity = property(...) # schedules an update for orientation

class ImageSprite(Sprite):
    # Upon creation sets representation to instance of ImageRepresentation
    # Mapping of texture->PositionableImageRepresentation so that representations are shared
    image = property(...)            # selects appropriate representation for image.texture
    tint_color = (1, 1, 1, 1)        # ignored if blend_color is not None
    blend_color = None               # 4-tuple of floats if not None

class AnimatedImageSprite(ImageSprite):
    # Upon creation sets representation to instance of AnimatedImageRepresentation and
    # also schedules an update method for self.time.
    # Use same texture->ImageSpriteRepresentation mapping as ImageSprite
    # Note that same class can also seamlessly use a non-animating image, slightly less efficiently.
    # Framerate, loop and timings are ignored if self.representation.texture is Texture not TextureSequence.
    loop = True                      # if True, modulo self.time by sequence time
    period = 0.25                    # ignored if self.timings is not None, otherwise gives seconds btwn frames      
    timings = None                   # optional sequence of (index, time), where index is into image
                                     # sequence and time is number of seconds of that image.

class TextSprite(Sprite):
    # Upon creation, sets representation to TextSpriteRepresentation (can probably keep class mapping on font)

    font = property(...)
    text = property(...)             # these two properties update the representation
    color = (1, 1, 1, 1)
    horizontal_alignment = 'left'
    vertical_alignment = 'baseline' 
    width = 0
    height = 0                       # set automatically whenever font or text changes; also, changing width
                                     # affects representation (wrapping)

class OwnerDrawSprite(Sprite):
    def draw(self):
         # abstract

class SpriteGroup(Sprite):
    children = []
    representation = GroupRepresentation()


# Geometry
# --------
 
class SpriteGeometry:
    center = Point2()
 
class RectGeometry(SpriteGeometry):
    left, top, right, bottom, topleft, topright, bottomleft, bottomright
 
class HexGeometry(SpriteGeometry):
    etc.


# Representations
# ---------------
 
class SpriteRepresentation:
    properties -> dict               # from XML file load of the SpriteRepresentation

    def draw(self, sprite):
         # Draw the given body at its position/orientation/time.
 
    def draw_many(self, sprite):
        # Draw a list of bodies at their positions/orientations/times.
        # Default implementation is:
        for body in bodies:
            self.draw(body)
 
class ImageSpriteRepresentation(SpriteRepresentation):
    texture = Texture()
 
    # draw_many can be optimised by binding texture / state once.
    # draw and draw_many assert isinstance(sprite, ImageSprite)
 
class AnimatedImageSpriteRepresentation(SpriteRepresentation):
    texture = UniformTextureSequence()  # or Texture, in which case this behaves same as ImageSpriteRepresentation
    timings = ...  (map time to sequence number: float or list or function?)
 
    # draw_many can be optimised by binding texture / state once.
    # draw and draw_many assert isinstance(sprite, AnimatedImageSprite)
 
class OwnerDrawSpriteRepresentation(SpriteRepresentation):
    # good for easy subclassing of Sprite.. no need to write a separate
    # representation class.  (but, no optimisation happens)
 
    # draw asserts isinstance(sprite, OwnerDrawSprite)
    # draw() calls sprite.draw().
 
# XXX name too similar to SpriteGeometry, but no relation.
class GeometrySpriteRepresentation(SpriteRepresentation):
    # draws a euclid geometry object (rectangle, circle, ellipse, ..)
 
class TextSpriteRepresentation(SpriteRepresentation):
    # self explanatory
 
class SpriteGroupRepresentation(SpriteRepresentation):
    # can only be attached to SpriteGroup.
 
    # draw asserts isinstance(sprite, SpriteGroup)
    # draw() applies transform in Sprite (and temporarily adds time to
    # children), then calls child.representation.draw(child) for each child.
 

# Controllers
# -----------
 
class SpriteLayer:
    def draw_all(self):
        # sort and group sprites on id(sprite.representation).  call draw_many
        # wherever the group has more than 1 sprite.
 
class Map:
    def draw(self):
        # sort and group cells on id(cell.tile.representation).  call draw_many
        # for list of cells wherever group has more than one cell.
 
    def collide(self, sprite):
        # Return Collision object for sprite against this map


# Collision interface:
# --------------------
 
class SpriteCollision:
    sprite1 -> Sprite
    sprite2 -> Sprite
 
    # These can all be lazily computed
    position -> Point2
    normal -> Vector2
    bounce_vector -> Vector2
    slide_vector -> Vector2
    impulse_vector -> Vector2
    overlap -> Rectangle
    penetration -> float
 
class SpriteCollider:
    # abstract
    def collide(self, sprite, other):
        # Return Collision2D object or None if no collision
        
class GeometrySpriteCollider:
    # Collides any euclid geometry with any other.  Returns False if other
    # collider is not geometry
 
class StencilSpriteCollider:
    # Collides by drawing representations to stencil buffer, querying overlap
    # count.   Only for newish video cards.. don't know how to fallback
    # efficiently.  Can collide with geometry if we have a way to draw
    # geometry.
</code>

Properties defined in XML files are loaded into:

  * attributes on Sprites. These may overwrite attributes already on the Sprite.
  * properties in Blueprints referenced by sprites in XML are loaded into blueprint dicts.

The same API can be regurgitated for 3D module:

<code python>
class Body:
    position = Vector3()
    scale = Vector3()
    orientation = Quaternion()
    time = float()

    representation = BodyRepresentation()
    collider = BodyCollider()

class BodyRepresentation:
    # abstract
    def draw(self, body):

    def draw_many(self, bodies):
        
class GeometryBodyRepresentation:
    # Draw a cube, sphere, torus, teapot, etc.

class MeshBodyRepresentation:
    # Draw a mesh loaded from .obj etc.

class SkeletonBodyRepresentation:
    # assumes bone structure and joint angles in body

class Collision3D:
    position -> Point3
    contacts -> sequence of Ray3
    normal -> Vector3
    bounce_vector -> Vector3
    slide_vector -> Vector3
    impulse_vector -> Vector3
    penetration -> float

class BodyCollider:
    # abstract
    def collide(self, body, other):
        ...

class GeometryBodyCollider:
    ...

class SeparatingPlanesCollider:
    ...

etc.

</code>

FAQ:
  * **How is this different to a scenegraph?**  No state (representation) sorting below children of root.  Actually, SpriteGroup //could// sort its children, but probably not worthwhile for the kinds of use-cases I'm thinking of; and children of one sprite group wouldn't be sorted amongst children of another (because transforms are applied using GL, not local matrix stack).
  * **What is benefit of separate SpriteRepresentation class, when most Sprite subclasses have their own representation?** Sorting can be done on representation rather than class (which wouldn't be valid when classes are extended) or method (which is unspeakable).  There are usecases for subclassing representation without subclassing sprite, and vice-versa (with benefit of code-reuse and performance, respectively).
  * **Isn't this too hard?**  Example animated sprite, tinted to 50% alpha::

        fire_filmstrip = load_image('fire.png')
        fire_sequence = Texture3D(ImageSequence(fire_filmstrip, 1,5))  # maybe, sequence api non-existant atm.
        sprite = AnimatedImageSprite(fire_sequence)
        sprite.tint_color = (1, 1, 1, .5)
        view.add(sprite)

  * **Isn't SpriteRepresentation a Drawable?**  Fulfils same role as OpenSceneGraph's Drawable; but we have to keep it specific to Sprites (unless sprites are unified with 3D, see top of section).
  * **What about display lists?** SpriteRepresentation is free to cache display lists on the sprite if it wants.  Would recommend ImageSpriteRepresentation, but not AnimatedImageSpriteRepresentation do this.


... you know we couldn't have UTF8 source code and use ∂x, ∂x, ω, ...
