class SpriteCollision:
    sprite1 -> Sprite
    sprite2 -> Sprite
 
    # These can all be lazily computed
    position -> Point2
    normal -> Vector2
    bounce_vector -> Vector2
    slide_vector -> Vector2
    impulse_vector -> Vector2
    overlap -> Rectangle
    penetration -> float
 
class SpriteCollider:
    # abstract
    def collide(self, sprite, other):
        # Return Collision2D object or None if no collision
        
class GeometrySpriteCollider:
    # Collides any euclid geometry with any other.  Returns False if other
    # collider is not geometry
 
class StencilSpriteCollider:
    # Collides by drawing representations to stencil buffer, querying overlap
    # count.   Only for newish video cards.. don't know how to fallback
    # efficiently.  Can collide with geometry if we have a way to draw
    # geometry.