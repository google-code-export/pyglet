#!/usr/bin/env python

'''Testing a sprite.

The ball should bounce off the sides of the window. You may resize the
window.

This test should just run without failing.
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import os
import unittest

from pyglet.gl import glClear
import pyglet.window
import pyglet.window.event
import pyglet.clock
from pyglet.image import load_image
from pyglet.sprite import ImageSprite, FlatView
from pyglet.sprite.camera import FlatCamera

ball_png = os.path.join(os.path.dirname(__file__), 'ball.png')

class FlatSpriteTest(unittest.TestCase):

    def test_sprite(self):
        w = pyglet.window.Window(width=320, height=320)

        image = load_image(ball_png)
        ball = ImageSprite(image)
        view = FlatView(0, 0, 320, 320, sprites=[ball])

        w.push_handlers(view.camera)

        dx, dy = (10, 5)

        clock = pyglet.clock.Clock(fps_limit=30)
        while not w.has_exit:
            clock.tick()
            w.dispatch_events()

            # move, check bounds
            ball.x += dx; ball.y += dy
            g = ball.geometry
            if g.left < 0: g.left = 0; dx = -dx
            elif g.right > w.width: g.right = w.width; dx = -dx
            if g.bottom < 0: g.bottom = 0; dy = -dy
            elif g.top > w.height: g.top = w.height; dy = -dy

            # keep our focus in the middle of the window
            view.fx = w.width/2
            view.fy = w.height/2

            view.clear()
            view.draw()
            w.flip()

        w.close()

if __name__ == '__main__':
    unittest.main()
