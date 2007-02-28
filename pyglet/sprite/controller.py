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