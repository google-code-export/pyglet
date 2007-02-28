import os
import math

import pyglet.window
from pyglet.window.event import *
from pyglet.window.key import *
import pyglet.clock
from pyglet.euclid import Vector2, Matrix3
from pyglet.image import *
from pyglet.sprite import *

class CarSprite(ImageSprite):
    speed = 0
    def update(self, dt):
        # handle input and move the car
        self.orientation += (keyboard[K_LEFT] - keyboard[K_RIGHT]) * 150 * dt
        self.speed += (keyboard[K_UP] - keyboard[K_DOWN]) * 75 
        if self.speed > 300: self.speed = 300
        if self.speed < -150: self.speed = -150
        r = Matrix3.new_rotate(math.radians(self.orientation))
        v = dt * self.speed * (r * Vector2(0, 1))
        self.position = self.position + v

w = pyglet.window.Window(width=512, height=512)
#w.set_exclusive_mouse()

# load the map and car and set up the scene and view
dirname = os.path.dirname(__file__)
m = RectMap.load_xml(os.path.join(dirname, 'road-map.xml'), 'map0')
m.z = 10
car = CarSprite(load_image(os.path.join(dirname, 'car.png')))
view = FlatView.from_window(w, layers=[m], sprites=[car])

keyboard = KeyboardStateHandler()
w.push_handlers(keyboard)

clock = pyglet.clock.Clock(fps_limit=30)
clock.schedule(car.update)

while not w.has_exit:
    dt = clock.tick()
    w.dispatch_events()

    # re-focus on the car
    view.fx, view.fy = car.geometry.center

    # draw
    view.draw()
    w.flip()
w.close()


