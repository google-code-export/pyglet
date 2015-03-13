See also the ReleaseSchedule for a more general wishlist.

**Porting projects**

  * Port pyglet to win64 (and test with a 64-bit Python build on Vista and XP/64).  This is probably a lot of tedious work in fixing up the type sizes throughout the Windows and COM code in pyglet (it's currently lazy about uses of int and long, and pointer sizes, for example).  Ideally there shouldn't need to be a platform split (i.e., just update the existing Windows code in-place).
  * Port pyglet on OS X to use Cocoa instead of Carbon.  The OS X Carbon API is deprecated, and cannot be used for 64-bit applications.  There are Python-Cocoa bindings provided with the Python OS X framework; but for users running a later version a raw PyObjC-based wrapper might need to be used.  This will definitely be a separate platform to "carbon" in pyglet source.  Test the port with a 64-bit Python on Leopard.

**Prototyping projects**

I'm not after a complete pyglet module here, as that requires extensive design prototyping as well.  The student project would be to create a series of example programs using ctypes that prototype the platform capability.

  * Prototype joystick support for Windows, OS X and Linux.  Ideally support analog and digital controllers, force feedback, device add/remove notification, and device query.  There may need to be several backends for Linux.
  * Prototype tablet support for Windows, OS X and Linux.  Ideally support multiple pens/erasers, tilt, pressure, and tablet buttons.