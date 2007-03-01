#!/usr/bin/env python

'''
Model code for managing rectangular and hexagonal maps
======================================================

This module provides classes for managing rectangular and hexagonal maps.

---------------
Getting Started
---------------

You may create a map interactively and query it:

TBD

'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import os
import math
import xml.dom
import xml.dom.minidom

from pyglet.resource import Resource, register_factory
from pyglet.sprite.geometry import *

@register_factory('rectmap')
def rectmap_factory(resource, tag):
    width, height = map(int, tag.getAttribute('tile_size').split('x'))
    origin = None
    if tag.hasAttribute('origin'):
        origin = map(int, tag.getAttribute('origin').split(','))
    id = tag.getAttribute('id')

    # now load the columns
    cells = []
    m = RectMap(id, width, height, cells, origin)
    resource.add_resource(id, m)
    from pyglet.sprite import ImageSprite
    for i, column in enumerate(tag.getElementsByTagName('column')):
        c = []
        cells.append(c)
        for j, cell in enumerate(column.getElementsByTagName('cell')):
            tile = resource.get_resource(cell.getAttribute('tile'))
            s = ImageSprite(tile)
            s.geometry_factory = m.geometry_factory
            s.i, s.j = i, j
            s.position = s.geometry.bottomleft
            # XXX 
            #s.blueprint = resource.handle_properties(image?)
            for name, value in resource.handle_properties(cell):
                setattr(s, name, value)
            c.append(s)
    return m

@register_factory('hexmap')
def hexmap_factory(resource, tag):
    height = int(tag.getAttribute('tile_height'))
    width = hex_width(height)
    origin = None
    if tag.hasAttribute('origin'):
        origin = map(int, tag.getAttribute('origin').split(','))
    id = tag.getAttribute('id')

    # now load the columns
    cells = []
    m = HexMap(id, height, cells, origin)
    resource.add_resource(id, m)
    from pyglet.sprite import ImageSprite
    for i, column in enumerate(tag.getElementsByTagName('column')):
        c = []
        cells.append(c)
        for j, cell in enumerate(column.getElementsByTagName('cell')):
            tile = resource.get_resource(cell.getAttribute('tile'))
            s = ImageSprite(tile)
            s.geometry_factory = m.geometry_factory
            s.i, s.j = i, j
            s.position = s.geometry.x, s.geometry.y
            # XXX 
            #s.blueprint = resource.handle_properties(image?)
            for name, value in resource.handle_properties(cell):
                setattr(s, name, value)
            c.append(s)
    return m

class Map(object):
    '''Base class for Maps.

    Both rect and hex maps have the following attributes:

        id              -- identifies the map in XML and Resources
        (width, height) -- size of map in cells
        (pxw, pxh)      -- size of map in pixels
        (tw, th)        -- size of each cell in pixels
        (x, y, z)       -- offset of map top left from origin in pixels
        cells           -- array [x][y] of Cell instances
    '''

class RegularTesselationMap(Map):
    '''A class of Map that has a regular array of Cells.
    '''
    def get_cell(self, i, j):
        ''' Return Cell at cell pos=(i, j).

        Return None if out of bounds.'''
        if i < 0 or j < 0:
            return None
        try:
            return self.cells[i][j]
        except IndexError:
            return None

class RectMap(RegularTesselationMap):
    '''Rectangular map.

    Cells are stored in column-major order with y increasing up,
    allowing [x][y] addressing:
    +---+---+---+
    | d | e | f |
    +---+---+---+
    | a | b | c |
    +---+---+---+
    Thus cells = [['a', 'd'], ['b', 'e'], ['c', 'f']]
    and cells[0][1] = 'd'
    '''
    def __init__(self, id, tw, th, cells, origin=None):
        self.id = id
        self.tw, self.th = tw, th
        if origin is None:
            origin = (0, 0, 0)
        self.x, self.y, self.z = origin
        self.cells = cells

    def get_pxw(self):
        return len(self.cells) * self.tw
    pxw = property(get_pxw)
    def get_pxh(self):
        return len(self.cells[0]) * self.th
    pxh = property(get_pxh)

    def get_in_region(self, x1, y1, x2, y2):
        '''Return cells (in [column][row]) that are within the
        pixel bounds specified by the bottom-left (x1, y1) and top-right
        (x2, y2) corners.

        '''
        x1 = max(0, x1 // self.tw)
        y1 = max(0, y1 // self.th)
        x2 = min(len(self.cells), x2 // self.tw + 1)
        y2 = min(len(self.cells[0]), y2 // self.th + 1)
        return [self.cells[x][y] for x in range(x1, x2) for y in range(y1, y2)]
 
    def get(self, x, y):
        ''' Return Cell at pixel px=(x,y).

        Return None if out of bounds.'''
        return self.get_cell(x // self.tw, y // self.th)
 
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    def get_neighbor(self, cell, direction):
        '''Get the neighbor Cell in the given direction (di, dj) which
        is one of self.UP, self.DOWN, self.LEFT or self.RIGHT.

        Returns None if out of bounds.
        '''
        di, dj = direction
        return self.get_cell(cell.i + di, cell.i + dj)

    @classmethod
    def load_xml(cls, filename, id):
        '''Load a map from the indicated XML file.

        Return a Map instance.'''
        return Resource.load(filename)[id]
 
    def geometry_factory(self, sprite):
        x = sprite.i * self.tw
        y = sprite.j * self.th
        return RectGeometry(sprite, x, y, self.tw, self.th)

class HexMap(RegularTesselationMap):
    '''Map with flat-top, regular hexagonal cells.

    Additional attributes extending MapBase:

        edge_length -- length of an edge in pixels

    Hexmaps store their cells in an offset array, column-major with y
    increasing up, such that a map:
          /d\ /h\
        /b\_/f\_/
        \_/c\_/g\
        /a\_/e\_/
        \_/ \_/ 
    has cells = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
    '''
    def __init__(self, id, th, cells, origin=None):
        self.id = id
        self.th = th
        if origin is None:
            origin = (0, 0, 0)
        self.x, self.y, self.z = origin
        self.cells = cells

        # figure some convenience values
        self.edge_length = int(th / math.sqrt(3))
        self.tw = self.edge_length * 2

    def get_pxw(self):
        s = self.edge_length
        return self.tw + (len(self.cells) - 1) * (s + s // 2)
    pxw = property(get_pxw)
    def get_pxh(self):
        pxh = len(self.cells[0]) * self.th
        if not len(self.cells) % 2:
            return pxh + (self.th // 2)
        return pxh
    pxh = property(get_pxh)

    def get_in_region(self, x1, y1, x2, y2):
        '''Return cells (in [column][row]) that are within the pixel bounds
        specified by the bottom-left (x1, y1) and top-right (x2, y2) corners.
        '''
        col_width = self.tw // 2 + self.tw // 4
        x1 = max(0, x1 // col_width)
        y1 = max(0, y1 // self.th - 1)
        x2 = min(len(self.cells), x2 // col_width + 1)
        y2 = min(len(self.cells[0]), y2 // self.th + 1)
        return [self.cells[x][y] for x in range(x1, x2) for y in range(y1, y2)]
 
    def get(self, x, y):
        '''Get the Cell at pixel px=(x,y).
        Return None if out of bounds.'''
        s = self.edge_length
        # map is divided into columns of
        # s/2 (shared), s, s/2(shared), s, s/2 (shared), ...
        x = x // (s/2 + s)
        if x % 2:
            # every second cell is up one
            y -= self.th // 2
        y = y // self.th
        return self.get_cell(x, y)

    UP = 'up'
    DOWN = 'down'
    UP_LEFT = 'up left'
    UP_RIGHT = 'up right'
    DOWN_LEFT = 'down left'
    DOWN_RIGHT = 'down right'
    def get_neighbor(self, cell, direction):
        '''Get the neighbor cell in the given direction which
        is one of self.UP, self.DOWN, self.UP_LEFT, self.UP_RIGHT,
        self.DOWN_LEFT or self.DOWN_RIGHT.

        Return None if out of bounds.
        '''
        if direction is self.UP:
            return self.get_cell(cell.i, cell.j + 1)
        elif direction is self.DOWN:
            return self.get_cell(cell.i, cell.j - 1)
        elif direction is self.UP_LEFT:
            if cell.i % 2:
                return self.get_cell(cell.i - 1, cell.j + 1)
            else:
                return self.get_cell(cell.i - 1, cell.j)
        elif direction is self.UP_RIGHT:
            if cell.i % 2:
                return self.get_cell(cell.i + 1, cell.j + 1)
            else:
                return self.get_cell(cell.i + 1, cell.j)
        elif direction is self.DOWN_LEFT:
            if cell.i % 2:
                return self.get_cell(cell.i - 1, cell.j)
            else:
                return self.get_cell(cell.i - 1, cell.j - 1)
        elif direction is self.DOWN_RIGHT:
            if cell.i % 2:
                return self.get_cell(cell.i + 1, cell.j)
            else:
                return self.get_cell(cell.i + 1, cell.j - 1)
        else:
            raise ValueError, 'Unknown direction %r'%direction

    def geometry_factory(self, sprite):
        x = sprite.i * (self.tw / 2 + self.tw // 4)
        y = sprite.j * self.th
        if sprite.i % 2:
            y += self.th // 2
        return HexGeometry(sprite, x, y, self.tw, self.th)

