## Current state ##

There is one playback implementation, using OpenAL 1.0 or 1.1.

There are two source implementations:

  * `riff` reads uncompressed WAV files
  * `avbin` uses AVbin to read many compressed audio and video files.

## Current limitations ##

Some codecs are not yet LGPL in FFmpeg, meaning they are not included with AVbin.  The ones you'll miss are:

  * AC3 (aka Dolby Surround).  This is nearly complete, actually; the author is trying to match performance with the old GPL implementation and improve downmixing.  Expect a release in one or two months.
  * AAC (aka MPEG-4).  There was a SOC project to LGPL this, but I'm not sure of its current status.

## Future work ##

  * Linux ALSA playback implementation is required as OpenAL is not installed by default on most distros, and because OpenAL on linux is still at version 1.0 (no stereo).
  * Windows DirectSound playback implementation is desirable as OpenAL is not installed by default.

There are no plans to write any more source implementations (for example, porting the old QuickTime, Gstreamer and DirectShow modules).

## Rationale for current implementation ##

The following is the old text of this page, describing the problems with other potential solutions on Linux, and why AVbin was created.

Gstreamer

  * Used in the old (er, current) pyglet.media implementation.  Available with most distros, albeit with some unknown quantity of codecs as these are installed separately.
  * Interface is Gobject-based and absurdly difficult to write for (see `pyglet/media/gstreamer.py` and `pyglet/media/gst_openal.py`).   I haven't yet had any success getting random access working (needed for seeking).
  * Heavy use of threads, and impossible (AFAICT) to control the rate of data.
  * Duration of media files is never given (this could be a bug in my implementation, but I've spent considerable time trying to work it out).
  * Process hangs if no codec can read the media (e.g. if you give it a text file).  Again, this could be an implementation error on my part.

libavcodec

  * Used by ffmpeg, mplayer, xine, vlc, etc.
  * No stable releases, ABI is constantly changing.  ABI changes occur even within the same build/version number.
  * Ubuntu does not include shared libraries, only static (this is the linking strategy recommended by the developers, and is why ABI is low priority).
  * Many distros (e.g. Fedora) do not include header files, so no chance of linking against the static libraries or determining ABI by some other means.

libvlc, libxine

  * Not ubiquitous; statically linked only.

libmad, libvorbis, libaudiofile, ...

  * Not ubiquitous due to prevalence of libavcodec these days.
  * No video support, limited audio file support.
  * Not really investigated feasibility yet.

PyMedia

  * Not ubiquitous.
  * Not really investigated feasibility yet.
  * LGPL