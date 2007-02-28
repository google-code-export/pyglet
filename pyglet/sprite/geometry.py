
class SpriteGeometry(object):
    '''Defines the shape of a sprite for the purposes of aligning the
    sprite with other objects in 2d space.

    Geometry is aligned around a center point.

    Attributes:
        `center` : Point2
           The center of the Geometry.
    '''

class RectGeometry(SpriteGeometry):
    '''A rectangle centered on "center".

    Attributes:
        center      -- (x, y)
        width       -- int width
        height      -- int height
        top         -- y extent
        bottom      -- y extent
        left        -- x extent
        right       -- x extent
        topleft     -- (x, y) of top-left corner
        topright    -- (x, y) of top-right corner
        bottomleft  -- (x, y) of bottom-left corner
        bottomright -- (x, y) of bottom-right corner
        midtop      -- (x, y) of middle of top side
        midbottom   -- (x, y) of middle of bottom side
        midleft     -- (x, y) of middle of left side
        midright    -- (x, y) of middle of right side
    '''
    def __init__(self, sprite, x, y, width, height):
        self.sprite = sprite
        self._x, self._y = x, y
        self.width, self.height = width, height

    def get_x(self):
        return self._x
    def set_x(self, x):
        self._x = self.sprite.x = x
    x = property(get_x, set_x)
    def get_y(self):
        return self._y
    def set_y(self, y):
        self._y = self.sprite.y = y
    y = property(get_y, set_y)

    def get_center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)
    def set_center(self, center):
        x, y = center
        self.x = x - self.width // 2
        self.y = y - self.height // 2
    center = property(get_center, set_center)
 
    # r/w, in pixels, y extent
    def get_top(self): return self.y + self.height
    def set_top(self, y): self.y = y - self.height
    top = property(get_top, set_top)

    # r/w, in pixels, y extent
    def get_bottom(self): return self.y
    def set_bottom(self, y): self.y = y
    bottom = property(get_bottom, set_bottom)

    # r/w, in pixels, x extent
    def get_left(self): return self.x
    def set_left(self, x): self.x = x
    left = property(get_left, set_left)

    # r/w, in pixels, x extent
    def get_right(self): return self.x + self.width
    def set_right(self, x): self.x = x - self.width
    right = property(get_right, set_right)

    # r/w, in pixels, (x, y)
    def get_midtop(self):
        return (self.x + self.width/2, self.y + self.height)
    def set_midtop(self, midtop):
        x, y = midtop
        self.x = x - self.width/2
        self.y = y - self.height
    midtop = property(get_midtop, set_midtop)

    # r/w, in pixels, (x, y)
    def get_midbottom(self):
        return (self.x + self.width/2, self.y)
    def set_midbottom(self, midbottom):
        x, y = midbottom
        self.x = x - self.width/2
        self.y = y
    midbottom = property(get_midbottom, set_midbottom)

    # r/w, in pixels, (x, y)
    def get_midleft(self):
        return (self.x, self.y + self.height/2)
    def set_midleft(self, midleft):
        x, y = midleft
        self.x = x
        self.y = y - self.height/2
    midleft = property(get_midleft, set_midleft)

    # r/w, in pixels, (x, y)
    def get_midright(self):
        return (self.x + self.width, self.y + self.height/2)
    def set_midright(self, midright):
        x, y = midright
        self.x = x - self.width
        self.y = y - self.height/2
    midright = property(get_midright, set_midright)
 
    # r/w, in pixels, (x, y)
    def get_topleft(self):
        return (self.x, self.y + self.height)
    def set_topleft(self, pos):
        x, y = pos
        self.x = x
        self.y = y - self.height
    topleft = property(get_topleft, set_topleft)
 
    # r/w, in pixels, (x, y)
    def get_topright(self):
        return (self.x + self.width, self.y + self.height)
    def set_topright(self, pos):
        x, y = pos
        self.x = x - self.width
        self.y = y - self.height
    topright = property(get_topright, set_topright)
 
    # r/w, in pixels, (x, y)
    def get_bottomright(self):
        return (self.x + self.width, self.y)
    def set_bottomright(self, pos):
        x, y = pos
        self.x = x - self.width
        self.y = y
    bottomright = property(get_bottomright, set_bottomright)
 
    # r/w, in pixels, (x, y)
    def get_bottomleft(self):
        return (self.x, self.y)
    def set_bottomleft(self, pos):
        self.x, self.y = pos
    bottomleft = property(get_bottomleft, set_bottomleft)



def hex_width(height):
    '''Determine a regular hexagon's width given its height.
    '''
    return int(height / math.sqrt(3)) * 2

# Note that we always add below (not subtract) so that we can try to
# avoid accumulation errors due to rounding ints. We do this so
# we can each point at the same position as a neighbor's corresponding
# point.
class HexGeometry(SpriteGeometry):
    '''A flat-top, regular hexagon centered on "center"

    Attributes:
        top             -- y extent
        bottom          -- y extent
        left            -- (x, y) of left corner
        right           -- (x, y) of right corner
        center          -- (x, y)
        topleft         -- (x, y) of top-left corner
        topright        -- (x, y) of top-right corner
        bottomleft      -- (x, y) of bottom-left corner
        bottomright     -- (x, y) of bottom-right corner
        midtop          -- (x, y) of middle of top side
        midbottom       -- (x, y) of middle of bottom side
        midtopleft      -- (x, y) of middle of left side
        midtopright     -- (x, y) of middle of right side
        midbottomleft   -- (x, y) of middle of left side
        midbottomright  -- (x, y) of middle of right side
    '''
    def __init__(self, sprite, x, y, width, height):
        self.sprite = sprite
        self.x, self.y = x, y
        self.width = width
        self.height = height

    # ro, side in pixels, y extent
    def get_top(self):
        return self.y + self.height
    top = property(get_top)

    # ro, side in pixels, y extent
    def get_bottom(self):
        return self.y
    bottom = property(get_bottom)

    # ro, in pixels, (x, y)
    def get_center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)
    center = property(get_center)

    # ro, mid-point in pixels, (x, y)
    def get_midtop(self):
        return (self.x + self.width // 2, self.y + self.height)
    midtop = property(get_midtop)

    # ro, mid-point in pixels, (x, y)
    def get_midbottom(self):
        return (self.x + self.width // 2, self.y)
    midbottom = property(get_midbottom)

    # ro, side in pixels, x extent
    def get_left(self):
        return (self.x, self.y + self.height // 2)
    left = property(get_left)

    # ro, side in pixels, x extent
    def get_right(self):
        return (self.x + self.width, self.y + self.height // 2)
    right = property(get_right)

    # ro, corner in pixels, (x, y)
    def get_topleft(self):
        return (self.x + self.width // 4, self.y + self.height)
    topleft = property(get_topleft)

    # ro, corner in pixels, (x, y)
    def get_topright(self):
        return (self.x + self.width // 2 + self.width // 4,
            self.y + self.height)
    topright = property(get_topright)

    # ro, corner in pixels, (x, y)
    def get_bottomleft(self):
        return (self.x + self.width // 4, self.y)
    bottomleft = property(get_bottomleft)

    # ro, corner in pixels, (x, y)
    def get_bottomright(self):
        return (self.x + self.width // 2 + self.width // 4, self.y)
    bottomright = property(get_bottomright)

    # ro, middle of side in pixels, (x, y)
    def get_midtopleft(self):
        return (self.x + self.width // 8,
            self.y + self.height // 2 + self.height // 4)
    midtopleft = property(get_midtopleft)

    # ro, middle of side in pixels, (x, y)
    def get_midtopright(self):
        return (self.x + self.width // 2 + self.width // 4 + self.width // 8,
            self.y + self.height // 2 + self.height // 4)
    midtopright = property(get_midtopright)

    # ro, middle of side in pixels, (x, y)
    def get_midbottomleft(self):
        return (self.x + self.width // 8, self.y + self.height // 4)
    midbottomleft = property(get_midbottomleft)

    # ro, middle of side in pixels, (x, y)
    def get_midbottomright(self):
        return (self.x + self.width // 2 + self.width // 4 + self.width // 8,
            self.y + self.height // 4)
    midbottomright = property(get_midbottomright)

