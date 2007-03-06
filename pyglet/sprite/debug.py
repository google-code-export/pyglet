#!/usr/bin/env python

'''
Simple images etc. to aid debugging
===================================

'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import math

from pyglet.sprite import *
from pyglet.image import *
from pyglet.gl import *

def brensenham_line(x, y, x2, y2):
    '''Modified to draw hex sides in HexCheckImage.
    
    Assumes dy > dx, x>x2 and y2>y which is always the case for what it's
    being used for.'''
    coords = []
    dx = abs(x2 - x)
    dy = abs(y2 - y)
    d = (2 * dx) - dy
    for i in range(0, dy):
        coords.append((x, y))
        while d >= 0:
            x -= 1
            d -= (2 * dy)
        y += 1
        d += (2 * dx)
    coords.append((x2,y2))
    return coords

class HexGeometryRepresentation(GeometrySpriteRepresentation):
    def __init__(self, height, color):
        self.height = height
        self.width = hex_width(height)
        self.color = color

        hg = HexGeometry(None, 0, 0, self.width, self.height)
        line = brensenham_line(*(hg.bottomleft + hg.left))
        mx = max([x for x,y in line])

        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)

        glBegin(GL_LINES)
        for x,y in line:
            glVertex2f(x, y)
            glVertex2f(self.width-x, y)
            if x:
                glVertex2f(mx-x, y + self.height/2)
                glVertex2f(self.width-mx+x, y + self.height/2)
        glEnd()

        glEndList()

    cache = {}

    # XXX hmmm
    @classmethod
    def new(cls, height, color):
        if height in cls.cache:
            return cls.cache[height]
        o = cls.cache[height] = cls(height, color)
        return o

    def key(self):
        return 'HexGeometryRepresentation', self.height, self.color

    def draw(self, sprite):

        # draw solid (not chewey) center
        # XXX push color state
        # XXX tint
        glColor4f(*[a*b for a,b in zip(self.color, sprite.tint_color)])
        glPushMatrix()
        glTranslatef(sprite.x, sprite.y, 0)
        glCallList(self.display_list)
        glPopMatrix()

def gen_hex_map(meta, h):
    r = []
    hm = HexMap('debug', h, r)
    COLOURS = [
        (.7, .7, .7, 1),
        (.9, .9, .9, 1),
        (1, 1, 1, 1)
    ]
    for i, m in enumerate(meta):
        c = []
        r.append(c)
        for j, info in enumerate(m):
            k = j
            if not i % 2:  k += 1
            cell = ImageSprite(HexGeometryRepresentation(h, COLOURS[k%3]),
                blueprint=info)
            cell.i, cell.j = i, j
            cell.geometry_factory = hm.geometry_factory
            cell.position = cell.geometry.x, cell.geometry.y
            c.append(cell)
    return hm

def gen_rect_map(meta, w, h):
    r = []
    rm = RectMap('debug', w, h, r)
    dark = SolidColorImagePattern((150, 150, 150, 255)).create_image(w, h)
    light = SolidColorImagePattern((200, 200, 200, 255)).create_image(w, h)
    for i, m in enumerate(meta):
        c = []
        r.append(c)
        for j, info in enumerate(m):
            if (i + j) % 2: image = dark
            else: image = light
            cell = ImageSprite(image, blueprint=info)
            cell.i, cell.j = i, j
            cell.geometry_factory = rm.geometry_factory
            cell.position = cell.geometry.bottomleft
            c.append(cell)
    return rm

def gen_recthex_map(meta, h):
    r = []
    w = hex_width(h)
    rm = RectMap('debug', w, h, r)
    dark = HexGeometryRepresentation(h, (.4, .4, .4, 1))
    light = HexGeometryRepresentation(h, (.7, .7, .7, 1))
    for i, m in enumerate(meta):
        c = []
        r.append(c)
        for j, info in enumerate(m):
            if (i + j) % 2: image = dark
            else: image = light
            cell = ImageSprite(image, blueprint=info)
            cell.i, cell.j = i, j
            cell.geometry_factory = rm.geometry_factory
            cell.position = cell.geometry.x, cell.geometry.y
            c.append(cell)
    return rm

