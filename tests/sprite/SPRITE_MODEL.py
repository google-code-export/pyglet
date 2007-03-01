#!/usr/bin/env python

'''Testing the sprite model.

This test should just run without failing.
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import unittest

from pyglet.window import Window
from pyglet.image import SolidColorImagePattern
from pyglet.sprite import ImageSprite

class SpriteModelTest(unittest.TestCase):

    def setUp(self):
        self.w = Window(width=1, height=1, visible=False)
        t = SolidColorImagePattern((0, 0, 0, 0)).create_image(10, 10).texture
        self.s = ImageSprite(t, position=(10,10))
        assert (self.s.geometry.x, self.s.geometry.y) == (10, 10)

    def tearDown(self):
        self.w.close()

    def test_top(self):
        assert self.s.geometry.top == 20
        self.s.geometry.top = 10
        assert (self.s.geometry.x, self.s.geometry.y) == (10, 0)

    def test_bottom(self):
        assert self.s.geometry.bottom == 10
        self.s.geometry.bottom = 0
        assert (self.s.geometry.x, self.s.geometry.y) == (10, 0)

    def test_right(self):
        assert self.s.geometry.right == 20
        self.s.geometry.right = 10
        assert (self.s.geometry.x, self.s.geometry.y) == (0, 10)

    def test_left(self):
        assert self.s.geometry.left == 10
        self.s.geometry.left = 0
        assert (self.s.geometry.x, self.s.geometry.y) == (0, 10)

    def test_center(self):
        assert self.s.geometry.center == (15, 15)
        self.s.geometry.center = (5, 5)
        assert (self.s.geometry.x, self.s.geometry.y) == (0, 0)

    def test_midtop(self):
        assert self.s.geometry.midtop == (15, 20)
        self.s.geometry.midtop = (5, 5)
        assert (self.s.geometry.x, self.s.geometry.y) == (0, -5)

    def test_midbottom(self):
        assert self.s.geometry.midbottom == (15, 10)
        self.s.geometry.midbottom = (5, 5)
        assert (self.s.geometry.x, self.s.geometry.y) == (0, 5)

    def test_midleft(self):
        assert self.s.geometry.midleft == (10, 15)
        self.s.geometry.midleft = (5, 5)
        assert (self.s.geometry.x, self.s.geometry.y) == (5, 0)

    def test_midright(self):
        assert self.s.geometry.midright == (20, 15)
        self.s.geometry.midright = (5, 5)
        assert (self.s.geometry.x, self.s.geometry.y) == (-5, 0)

    def test_topleft(self):
        assert self.s.geometry.topleft == (10, 20)
        self.s.geometry.topleft = (5, 5)
        assert (self.s.geometry.x, self.s.geometry.y) == (5, -5)

    def test_topright(self):
        assert self.s.geometry.topright == (20, 20)
        self.s.geometry.topright = (5, 5)
        assert (self.s.geometry.x, self.s.geometry.y) == (-5, -5)

    def test_bottomright(self):
        assert self.s.geometry.bottomright == (20, 10)
        self.s.geometry.bottomright = (5, 5)
        assert (self.s.geometry.x, self.s.geometry.y) == (-5, 5)

    def test_bottomleft(self):
        assert self.s.geometry.bottomleft == (10, 10)
        self.s.geometry.bottomleft = (5, 5)
        assert (self.s.geometry.x, self.s.geometry.y) == (5, 5)

if __name__ == '__main__':
    unittest.main()
