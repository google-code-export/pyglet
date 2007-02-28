# Lots Of Sprites

'''
Results (us per sprite per frame):
sprites  AMD64/mesa   AMD64/nv6.6k   MacBook Pro   AMD/nv7.8k
2000     28.3         29.3          20.6          22.0

after __slots__ removal
sprites  AMD64/mesa   AMD64/nv6.6k   MacBook Pro   AMD/nv7.8k
2000
'''

import os
import sys
import random

from pyglet.window import Window
from pyglet.clock import Clock
from pyglet.sprite import *
from pyglet.image import *
from pyglet.euclid import *
from pyglet.gl import *

w = Window(600, 600, vsync=False)

dirname = os.path.dirname(__file__)
img = load_image(os.path.join(dirname, 'car.png'))

class BouncySprite(ImageSprite):
    dx = dy = 0
    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.x < 0: self.x = 0; self.dx *= -1
        elif self.x > 580: self.x = 580; self.dx *= -1
        if self.y < 0: self.y = 0; self.dy *= -1
        elif self.y > 580: self.y = 580; self.dy *= -1

sprites = []
numsprites = int(sys.argv[1])
for i in range(numsprites):
    p = Point2(random.randint(0, w.width-img.width),
        random.randint(0, w.height-img.height))
    s = BouncySprite(img.texture, p)
    s.velocity = Vector2(random.randint(-10, 10), random.randint(-10, 10))
    sprites.append(s)

view = FlatView.from_window(w, sprites=sprites)
view.fx, view.fy = w.width/2, w.height/2

clock = Clock()
t = 0
numframes = 0
while 1:
    if w.has_exit:
        print 'FPS:', clock.get_fps()
        print 'us per sprite:', float(t) / (numsprites * numframes) * 1000000
        break
    t += clock.tick()
    w.dispatch_events()
    for s in sprites: s.update()
    view.clear()
    view.draw()
    w.flip()
    numframes += 1
w.close()


