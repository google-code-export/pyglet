## 1.2 ##

  * pyglet.media multithread changes
    * ~~Allow per-player silent driver~~
    * ~~Add sync groups for players~~
    * ~~Looping sources~~
    * ~~PulseAudio volume~~ etc, maybe 3D emul.
    * Upgrade RIFF source
    * Pulse unknown timestamp -> None
    * Backward compat to dispatch\_events
    * Backward compat source/player API
    * Document SourceGroup and other new MT behaviour
    * Discover cause of avbin segfaults on linux
    * Example with many players
    * Fix play/pause button in media\_player example
    * ~~~Update docs s/ALSA/PulseAudio~~~
  * pyglet.input
    * Document
    * Better joystick example
    * Better apple remote example
    * Standard key and button names
    * DirectInput: convert signed relative values
    * Check multiple mouse/keyboard behaviour
  * ~~pyglet.libs~~
  * pyglet.window/gl/canvas refactor
    * Embedding example
    * Fix documentation
  * pyglet.app
    * Fix exit loop carnage
    * Fix clock/idle/sleep mess
    * Standardised wait/file objects
    * Split user/system event loop for subclassing
    * Step method
    * Some way to force another iteration (for Window.invalid)
    * Document MT features
  * pyglet.image/graphics
    * Do texture/buffer frees at allocation time instead of context switch?

Text/layout:
  * Richard wants paragraph background colors / borders
  * ~~Joseph wants character wrapping for overlong words~~


## Wishlist ##

Some ideas that have been kicking round.  No guarantee they will ever appear.  Patches not necessarily welcome (but please find out!).

  * pyglet.font:
    * Pairwise kerning
    * Enumerate installed fonts
    * Select a default font by style (serif, sans-serif, monospace)
    * Vertical fonts
    * Load font by filename (instead of current two-step process).
    * Get the OS to draw entire line of text at a time (optionally).  On Mac this would give access to advanced type features (e.g. Zapfino).  On Mac and Windows we would get subpixel antialiasing (RGB decimated).  Use some sort of texture paging mechanism to update and reuse textures as needed.  Keep track of glyph positions within the rendering for text motion/select support (see above).  (What about style runs?).
  * pyglet.text:
    * BIDI
    * HTML stylesheets (CSS or otherwise)
    * ReST documents
    * Save formatted documents
  * _pyglet.platform_
    * Determine registered file types/handlers/icons
    * Activate/disable screensaver
    * Clipboard, drag/drop, file accept
    * O/S dialogs (file open, save, ...)
    * Determine user preference for mouse double-click threshold
  * _pyglet.input_
    * tablet input
  * pyglet.media
    * Audio capture
    * Video capture
    * Audio surround files
    * Reintroduce QuickTime, GStreamer, DirectShow sources as alternatives to AVbin.  Perhaps allow them to manage their own playback of audio-only streams (foolproof and efficient, but less flexible).
  * pyglet.window
    * Support more than 3 mouse buttons
    * Window modality
    * Screen resolution/mode switch
    * Platform-provided message box (non-OpenGL.. good for errors, especially at startup) -- pyembryo already implements this.
    * Platform-drawn menubar (especially Mac) and pop-up menus.
    * Adjust RAMDAC LUT (for gamma ramp, etc).
    * Refactor GLX/AGL/WGL setup out of windowing/events code; make it easier to embed a pyglet canvas in other GUI toolkits (see experimental/wxtest.py for example).
    * Borderless window with taskbar entry (for owner-drawn decorations)
    * Translucent/non-rectangular windows.
    * Query screen refresh rate
  * pyglet.image
    * HDR textures (.tif, .hdr)
    * Cubemaps, volume, depth textures in DDS
    * AbstractImage to/from PIL image.
  * ... more ideas?