This document is a place to collate ideas - most of them not fully-formed.


# Maps #

Features:

  * images should be optional (map just contains meta-data)
  * additional properties (complex or just a number from a pixmap)
  * collision or not
  * allow height values  (which offset from the map's base height)
  * hexagons (flat-top only), squares
  * frustum/viewport culling
  * scrolling (duke nukem) or paged (zelda) or both (captain comic)
  * "Atlas" which will split up an incoming map source (image?) into multiple tile maps
  * play well with pathfinding code
  * query for tile at given position (transformed by viewport)

```
class Map:
    elements =                      # meta-data as dict? array?
    images =                        # images as dict? array?
    size = (x, y)                   # size of map in elements
    element_size = (x, y)           # size of each element in pixels
    origin = (x, y, z)              # offset of map top left from
                                    # origin in pixels

    def get_at(self, pos=(x,y), px=(x,y)):
        ' return Tile at tile pos or pixel pos '

    def get_neighbor(self, tile, direction):
        ' return coords of the neighbor of (x,y) in the given direction '

class HexMap:
    # same attrs / method signature as Map

class Tile:
    position = (x,y)        # in tile coords
    size = (w, h)           # in pixels
    top = property()        # ro, side in pixels, y extent
    bottom = property()     # ro, side in pixels, y extent
    left = property()       # ro, side in pixels, x extent
    right = property()      # ro, side in pixels, x extent
    center = property()     # ro, in pixels, (x, y)
    midtop = property()     # ro, in pixels, (x, y)
    midbottom = property()  # ro, in pixels, (x, y)
    midleft = property()    # ro, in pixels, (x, y)
    midright = property()   # ro, in pixels, (x, y)
    image =                 # optional
    properties = {}

class HexTile:
    position = (x,y)            # in tile coords
    size = (w, h)               # in pixels
    top = property()            # ro, side in pixels, y extent
    bottom = property()         # ro, side in pixels, y extent
    left = property()           # ro, corner in pixels, x extent
    right = property()          # ro, corner in pixels, x extent
    center = property()         # ro, in pixels, (x, y)
    midtop = property()         # ro, in pixels, (x, y)
    midbottom = property()      # ro, in pixels, (x, y)
    midtopleft = property()     # ro, in pixels, (x, y)
    midbottomleft = property()  # ro, in pixels, (x, y)
    midtopright = property()    # ro, in pixels, (x, y)
    midbottomright = property() # ro, in pixels, (x, y)
    image =                     # optional
    properties = {}
```


# Scene #

  * organises layers of maps / sprites
  * farms out updating for animations
  * handles global collision detection
  * map initialisation? positioning of sprites
  * simple state machine

```
class Scene:
    maps =                          # list of maps
    sprites =                       # list of sprites in ('group': list}
```


# Rendering #

  * top-down ("flat")
  * axiometric (with supplied scaling for each axis - eg isometric / dimetric)
  * persepctive
  * handles layers of sprites/tiles

```
class FlatRenderer:
    viewport = (x, y, w, h)     # origin, dimensions
    allow_oob = False
    scale = 1
    scene =                     # Scene instance
    rotation =

    def draw(self, position):

    def tile_at(self, (x, y)):
        ' query for tile at given screen pixel position '

    def sprite_at(self, (x, y)):
        ' query for sprite at given screen pixel position '

class AxiometricRenderer:
    viewport = (x, y, w, h)     # origin, dimensions
    allow_oob = False
    scale = (x, y, z, w)        # per-axis scaling
    scene =                     # Scene instance
    rotation =

    def draw(self, position):

    def sprite_at(self, (x, y)):
        ' query for sprite at given screen pixel position '

class PerspectiveRenderer:
    viewport = (x, y, w, h)     # origin, dimensions
    allow_oob = False
    scale = 1
    eye_offset = (x, y, z)      # offset from render position
    scene =                     # Scene instance
    rotation =

    def draw(self, position):
```

allow\_oob (_) indicates whether the viewport will allow viewing of
out-of-bounds tile positions (ie. for which there is no tile image). If set
to False then the map will not scroll to attempt to display oob tiles._


# Sprites #

  * separate collision/drawing geometry (might be image, or bounding box, or sphere, etc)
  * each image/frame has an anchor, which may be outside image bounds (makes walk cycle easier)
  * attach path animation / ai.
  * can be used as particles (abstract away the rendering so it can be batched)
  * make it easy to animate smoothly from one tile (or position) to another
  * have depth which is used to sort them into the display with any tile
  * layers
  * animation queue and optional cycles

```
class SpriteBase:
    position = (x, y, z)        # in pixels
    size = (w, h)               # in pixels   (depth?)
    orientation =               # HORIZONTAL or VERTICAL
    image =                     # image or animation to render
    image_offset = (x, y)       # offset of image to sprite position
    animations = []             # queue of animations to run

    def push_animation(self, animation):
        ''' push a SpriteAnimation onto this sprite's animation queue '''

    def cancel_animation(self):
        ' cancel the current animation being run '

    def clear_animation(self):
        ' clear the animation queue '

    def animate(self, dt):
        ' animate this sprite to handle passing of dt time '

class Sprite(SpriteBase):
    top = property()            # r/w, in pixels, y extent
    bottom = property()         # r/w, in pixels, y extent
    left = property()           # r/w, in pixels, x extent
    right = property()          # r/w, in pixels, x extent
    center = property()         # r/w, in pixels, (x, y)
    midtop = property()         # r/w, in pixels, (x, y)
    midleft = property()        # r/w, in pixels, (x, y)
    midright = property()       # r/w, in pixels, (x, y)
    midbottom = property()      # r/w, in pixels, (x, y)

class HexSprite(SpriteBase):
    top = property()            # r/w, side in pixels, y extent
    bottom = property()         # r/w, side in pixels, y extent
    left = property()           # r/w, corner in pixels, x extent
    right = property()          # r/w, corner in pixels, x extent
    center = property()         # r/w, in pixels, (x, y)
    midtop = property()         # r/w, in pixels, (x, y)
    midbottom = property()      # r/w, in pixels, (x, y)
    midtopleft = property()     # r/w, in pixels, (x, y)
    midbottomleft = property()  # r/w, in pixels, (x, y)
    midtopright = property()    # r/w, in pixels, (x, y)
    midbottomright = property() # r/w, in pixels, (x, y)

class SpriteAnimation:
    def animate(self, sprite, dt):
        ''' run this animation to handle passing of dt time. alters sprite
        position and optionally image '''

class JumpAnimation(SpriteAnimation):
    velocity = (vx, vy)         # in pixels / second?
    gravity =                   # in pixels / second?
    image =                     # optional ImageAnimation to run

class PathAnimation(SpriteAnimation):
    ''' Will animate smoothly from one position to another, optionallyo to
    another, optionally accelerating, etc. '''
    points = [(x, y, z)]        # points to move to in order
    speed =                     # initial speed in direction of first point
    velocity =                  # initial velocity if not in ^^^
    turn_speed =                # optional speed to slow to for turning
    acceleration =              # needed if turn_speed != None
    max_speed =                 # needed if acceleration != None
```


# Animated Images #

To support animating sprite images, we need animated images too:

  * animate
  * should be easy to do effects, like fade it in, flash it five times, glow, etc. (Behaviour class in Brains does this).
  * can be constructed from an Atlas or multiple Images.. set individual frame periods

```
class ImageAnimation(Image):
    source_frames =             # image frames to display
    timings =                   # seconds to display each image frame for
    cycle = False               # run through once or cycle?

    def animate(self, dt):
        ''' Run this animation to handle passing of dt time. Returns image
        to display '''

    def draw(self):

    @classmethod
    def from_files
    def from_atlas

class RGBAImageAnimation(Image):
    out = False                 # fade in or out (initially if cycle)
    cycle = 0                   # number of in/out cycles
    in_pause = 0                # seconds to pause at "in" peak
    out_pause = 0               # seconds to pause at "out" peak
    fade_time = 5               # seconds to fade over
    in_alpha = 1                # alpha when faded in
    out_alpha = 0               # ... when faded out
    in_colour = None            # solid colour when "faded in"
    out_colour = None           # ... when "faded out"

    def animate(self, dt):
        ''' Run this animation to handle passing of dt time. Returns image
        to display '''

    def draw(self):

```

Possible usages:

Fade in from alpha 0 to 1:
```
   RGBAImageAnimation(image)
```

Flash image 5 times, once per second:
```
   RGBAImageAnimation(image, cycle=5, in_pause=.5, out_pause=.5, fade_time=0)
```

Fade the image out while also flashing the image to white:
```
   RGBAImageAnimation(RGBAImageAnimation(image, out_color=(1,1,1),
        flash_time=1, cycle=100, out_alpha=1, out=True), out=True)
```

# Use cases #

  * side/up scroller shmup (map auto scroll, free movement, parallax)
  * platformer (map paging, partial scroll, free movement with obstacles)
  * hexagonal strategy game incl. piece placement on tile borders, stacked units
  * top-down roguelike (fixed cell movement, squares, special tiles)
  * top-down RPG (free movement, squares, special tiles)
  * top-down RTS (free movement, hexagonal, regions)
  * walls/platforms for isometric (that exploding game by phil)
  * full heightmap w/ gradients (simcity 2000, though with smooth blending between levels)




# Grid Sizes #

Separate model (tile space, sprite positioning, etc) from view space (pixels on screen) though there would still be a pixel quantum in the model space.

  * sub-pixels?         (would anyone ever need this?
  * pixels
  * movement quanta     (pixel, sub-tile or tile)
  * map masks           (sub-tile but > movement quanta)
  * info grids          (usually tile size)
  * tile size(s)        (multiple tile sizes possible?)
  * tile regions?       ("amount of wheat"?)
  * screen size
  * maps                (transitions between levels?)
