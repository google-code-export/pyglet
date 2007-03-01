#!/usr/bin/env python

'''Testing the map model.

This test should just run without failing.
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import unittest

from pyglet.window import Window
from pyglet.sprite import RectMap, HexMap
from pyglet.sprite.debug import gen_hex_map, gen_rect_map

rmd = [
   [ {'meta': x} for x in m ] for m in ['ad', 'be', 'cf']
]
hmd = [
   [ {'meta': x} for x in m ] for m in ['ab', 'cd', 'ef', 'gh']
]

class MapModelTest(unittest.TestCase):
    def setUp(self):
        self.w = Window(width=1, height=1, visible=False)

    def tearDown(self):
        self.w.close()

    def test_rect_neighbor(self):
        # test rectangular tile map
        #    +---+---+---+
        #    | d | e | f |
        #    +---+---+---+
        #    | a | b | c |
        #    +---+---+---+
        m = gen_rect_map(rmd, 10, 16)
        t = m.get_cell(0,0)
        assert (t.i, t.j) == (0, 0) and t.meta == 'a'
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEquals(m.get_neighbor(t, m.UP).meta, 'd')
        assert m.get_neighbor(t, m.LEFT) is None
        self.assertEquals(m.get_neighbor(t, m.RIGHT).meta, 'b')
        t = m.get_neighbor(t, m.UP)
        assert (t.i, t.j) == (0, 1) and t.meta == 'd'
        self.assertEquals(m.get_neighbor(t, m.DOWN).meta, 'a')
        assert m.get_neighbor(t, m.UP) is None
        assert m.get_neighbor(t, m.LEFT) is None
        self.assertEquals(m.get_neighbor(t, m.RIGHT).meta, 'e')
        t = m.get_neighbor(t, m.RIGHT)
        assert (t.i, t.j) == (1, 1) and t.meta == 'e'
        self.assertEquals(m.get_neighbor(t, m.DOWN).meta, 'b')
        assert m.get_neighbor(t, m.UP) is None
        self.assertEquals(m.get_neighbor(t, m.RIGHT).meta, 'f')
        self.assertEquals(m.get_neighbor(t, m.LEFT).meta, 'd')
        t = m.get_neighbor(t, m.RIGHT)
        assert (t.i, t.j) == (2, 1) and t.meta == 'f'
        self.assertEquals(m.get_neighbor(t, m.DOWN).meta, 'c')
        assert m.get_neighbor(t, m.UP) is None
        assert m.get_neighbor(t, m.RIGHT) is None
        self.assertEquals(m.get_neighbor(t, m.LEFT).meta, 'e')
        t = m.get_neighbor(t, m.DOWN)
        assert (t.i, t.j) == (2, 0) and t.meta == 'c'
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEquals(m.get_neighbor(t, m.UP).meta, 'f')
        assert m.get_neighbor(t, m.RIGHT) is None
        self.assertEquals(m.get_neighbor(t, m.LEFT).meta, 'b')

    def test_rect_coords(self):
        # test rectangular tile map
        #    +---+---+---+
        #    | d | e | f |
        #    +---+---+---+
        #    | a | b | c |
        #    +---+---+---+
        m = gen_rect_map(rmd, 10, 16)

        # test tile sides / corners
        t = m.get_cell(0,0)
        assert t.geometry.top == 16
        assert t.geometry.bottom == 0
        assert t.geometry.left == 0
        assert t.geometry.right == 10
        assert t.geometry.topleft == (0, 16)
        assert t.geometry.topright == (10, 16)
        assert t.geometry.bottomleft == (0, 0)
        assert t.geometry.bottomright == (10, 0)
        assert t.geometry.midtop == (5, 16)
        assert t.geometry.midleft == (0, 8)
        assert t.geometry.midright == (10, 8)
        assert t.geometry.midbottom == (5, 0)

    def test_rect_pixel(self):
        # test rectangular tile map
        #    +---+---+---+
        #    | d | e | f |
        #    +---+---+---+
        #    | a | b | c |
        #    +---+---+---+
        m = gen_rect_map(rmd, 10, 16)
        t = m.get(0,0)
        assert (t.x, t.y) == (0, 0) and t.meta == 'a'
        t = m.get(9,15)
        assert (t.x, t.y) == (0, 0) and t.meta == 'a'
        t = m.get(10,15)
        assert (t.x, t.y) == (1, 0) and t.meta == 'b'
        t = m.get(9,16)
        assert (t.x, t.y) == (0, 1) and t.meta == 'd'
        t = m.get(10,16)
        assert (t.x, t.y) == (1, 1) and t.meta == 'e'

    def test_hex_neighbor(self):
        # test hexagonal tile map
        # tiles = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
        #   /d\ /h\
        # /b\_/f\_/
        # \_/c\_/g\
        # /a\_/e\_/
        # \_/ \_/ 
        m = gen_hex_map(hmd, 32)
        t = m.get_cell(0,0)
        assert (t.i, t.j) == (0, 0) and t.meta == 'a'
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEquals(m.get_neighbor(t, m.UP).meta, 'b')
        assert m.get_neighbor(t, m.DOWN_LEFT) is None
        assert m.get_neighbor(t, m.DOWN_RIGHT) is None
        assert m.get_neighbor(t, m.UP_LEFT) is None
        self.assertEquals(m.get_neighbor(t, m.UP_RIGHT).meta, 'c')
        t = m.get_neighbor(t, m.UP)
        assert (t.i, t.j) == (0, 1) and t.meta == 'b'
        self.assertEquals(m.get_neighbor(t, m.DOWN).meta, 'a')
        assert m.get_neighbor(t, m.UP) is None
        assert m.get_neighbor(t, m.DOWN_LEFT) is None
        self.assertEquals(m.get_neighbor(t, m.DOWN_RIGHT).meta, 'c')
        assert m.get_neighbor(t, m.UP_LEFT) is None
        self.assertEquals(m.get_neighbor(t, m.UP_RIGHT).meta, 'd')
        t = m.get_neighbor(t, m.DOWN_RIGHT)
        assert (t.i, t.j) == (1, 0) and t.meta == 'c'
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEquals(m.get_neighbor(t, m.UP).meta, 'd')
        self.assertEquals(m.get_neighbor(t, m.DOWN_LEFT).meta, 'a')
        self.assertEquals(m.get_neighbor(t, m.DOWN_RIGHT).meta, 'e')
        self.assertEquals(m.get_neighbor(t, m.UP_LEFT).meta, 'b')
        self.assertEquals(m.get_neighbor(t, m.UP_RIGHT).meta, 'f')
        t = m.get_neighbor(t, m.UP_RIGHT)
        assert (t.i, t.j) == (2, 1) and t.meta == 'f'
        self.assertEquals(m.get_neighbor(t, m.DOWN).meta, 'e')
        assert m.get_neighbor(t, m.UP) is None
        self.assertEquals(m.get_neighbor(t, m.DOWN_LEFT).meta, 'c')
        self.assertEquals(m.get_neighbor(t, m.DOWN_RIGHT).meta, 'g')
        self.assertEquals(m.get_neighbor(t, m.UP_LEFT).meta, 'd')
        self.assertEquals(m.get_neighbor(t, m.UP_RIGHT).meta, 'h')
        t = m.get_neighbor(t, m.DOWN_RIGHT)
        assert (t.i, t.j) == (3, 0) and t.meta == 'g'
        assert m.get_neighbor(t, m.DOWN) is None
        self.assertEquals(m.get_neighbor(t, m.UP).meta, 'h')
        self.assertEquals(m.get_neighbor(t, m.DOWN_LEFT).meta, 'e')
        assert m.get_neighbor(t, m.DOWN_RIGHT) is None
        self.assertEquals(m.get_neighbor(t, m.UP_LEFT).meta, 'f')
        assert m.get_neighbor(t, m.UP_RIGHT) is None
        t = m.get_neighbor(t, m.UP)
        assert (t.i, t.j) == (3, 1) and t.meta == 'h'
        self.assertEquals(m.get_neighbor(t, m.DOWN).meta, 'g')
        assert m.get_neighbor(t, m.UP) is None
        self.assertEquals(m.get_neighbor(t, m.DOWN_LEFT).meta, 'f')
        assert m.get_neighbor(t, m.DOWN_RIGHT) is None
        assert m.get_neighbor(t, m.UP_LEFT) is None
        assert m.get_neighbor(t, m.UP_RIGHT) is None

    def test_hex_coords(self):
        # test hexagonal tile map
        # tiles = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
        #   /d\ /h\
        # /b\_/f\_/
        # \_/c\_/g\
        # /a\_/e\_/
        # \_/ \_/ 
        m = gen_hex_map(hmd, 32)

        # test tile sides / corners
        t00 = m.get_cell(0, 0)
        assert t00.geometry.top == 32
        assert t00.geometry.bottom == 0
        assert t00.geometry.left == (0, 16)
        assert t00.geometry.right == (36, 16)
        assert t00.geometry.center == (18, 16)
        assert t00.geometry.topleft == (9, 32)
        assert t00.geometry.topright == (27, 32)
        assert t00.geometry.bottomleft == (9, 0)
        assert t00.geometry.bottomright == (27, 0)
        assert t00.geometry.midtop == (18, 32)
        assert t00.geometry.midbottom == (18, 0)
        assert t00.geometry.midtopleft == (4, 24)
        assert t00.geometry.midtopright == (31, 24)
        assert t00.geometry.midbottomleft == (4, 8)
        assert t00.geometry.midbottomright == (31, 8)

        t10 = m.get_cell(1, 0)
        assert t10.geometry.top == 48
        assert t10.geometry.bottom == 16
        assert t10.geometry.left == t00.geometry.topright
        assert t10.geometry.right == (63, 32)
        assert t10.geometry.center == (45, 32)
        assert t10.geometry.topleft == (36, 48)
        assert t10.geometry.topright == (54, 48)
        assert t10.geometry.bottomleft == t00.geometry.right
        assert t10.geometry.bottomright == (54, 16)
        assert t10.geometry.midtop == (45, 48)
        assert t10.geometry.midbottom == (45, 16)
        assert t10.geometry.midtopleft == (31, 40)
        assert t10.geometry.midtopright == (58, 40)
        assert t10.geometry.midbottomleft == t00.geometry.midtopright
        assert t10.geometry.midbottomright == (58, 24)

        t = m.get_cell(2, 0)
        assert t.geometry.top == 32
        assert t.geometry.bottom == 0
        assert t.geometry.left == t10.geometry.bottomright
        assert t.geometry.right == (90, 16)
        assert t.geometry.center == (72, 16)
        assert t.geometry.topleft == t10.geometry.right
        assert t.geometry.midtopleft == t10.geometry.midbottomright

    def test_hex_pixel(self):
        # test hexagonal tile map
        # tiles = [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g', 'h']]
        #   /d\ /h\
        # /b\_/f\_/
        # \_/c\_/g\
        # /a\_/e\_/
        # \_/ \_/ 
        m = gen_hex_map(hmd, 32)
        t = m.get(0,0)
        assert t is None
        t = m.get(0,16)
        assert (t.x, t.y) == (0, 0) and t.meta == 'a'
        t = m.get(16,16)
        assert (t.x, t.y) == (0, 0) and t.meta == 'a'
        t = m.get(35,16)
        assert (t.x, t.y) == (0, 0) and t.meta == 'a'
        t = m.get(36,16)
        assert (t.x, t.y) == (1, 0) and t.meta == 'c'

    def test_hex_dimensions(self):
        m = gen_hex_map([[{'a':'a'}]], 32)
        assert m.pxw, m.pxh == (36, 32)
        m = gen_hex_map([[{'a':'a'}]*2], 32)
        assert m.pxw, m.pxh == (36, 64)
        m = gen_hex_map([[{'a':'a'}]]*2, 32)
        assert m.pxw, m.pxh == (63, 48)

if __name__ == '__main__':
    unittest.main()
