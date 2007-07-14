#!/usr/bin/python
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2007 Alex Holkner
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
# $Id$

'''Audio and video playback.
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id$'

import sys

from pyglet import event

class MediaException(Exception):
    pass

class CannotSeekException(MediaException):
    pass

class Source(object):
    '''An audio and/or video source.

    :Ivariables:
        `audio_properties` : dict
            TODO
        `video_properties` : dict
            TODO
    '''

    _duration = None
    
    has_audio = False
    has_video = False

    def _get_duration(self):
        return self._duration

    duration = property(lambda self: self._get_duration(),
                        doc='''The length of the source, in seconds.

        Not all source durations can be determined; in this case the value
        is None.

        Read-only.

        :type: float
        ''')

    def play(self):
        '''Play the source.

        This is a convenience method which creates a ManagedSoundPlayer for
        this source and plays it immediately.

        :rtype: `ManagedSoundPlayer`
        '''
        player = ManagedSoundPlayer()
        player.queue(self)
        player.play()
        return player

    # Internal methods that Players call on the source:

    def _play(self):
        '''Begin decoding in real-time.'''
        pass

    def _pause(self):
        '''Pause decoding, but remain prerolled.'''
        pass

    def _stop(self):
        '''Stop forever and clean up.'''
        pass

    def _seek(self, timestamp):
        '''Seek to given timestamp.'''
        raise CannotSeekException()

    def _openal_get_buffer(self):
        '''Return buffer, or None if no more buffers.'''
        raise NotImplementedError(
            '%s does not support OpenAL.' % self.__class__.__name__)

    def _openal_release_buffer(self, buffer):
        '''Release a buffer.'''
        raise RuntimeError(
            '%s does not manage OpenAL buffers.' % self.__class__.__name__)

    def _directsound_fill_buffer(self, ptr1, len1, ptr2, len2):
        '''Fill ptr1 and ptr2 up with audio data.  Returns new write pointer.
        '''
        raise NotImplementedError(
            '%s does not support DirectX.' % self.__class__.__name__)

    def _alsa_fill_buffer(self, alsa_info):
        '''Fill ALSA buffer with data (interface TODO).'''
        raise NotImplementedError(
            '%s does not support ALSA.' % self.__class__.__name__)

    def _init_texture(self, player):
        '''Create the player's texture.'''
        pass

    def _update_texture(self, player, timestamp):
        '''Update the texture on player.'''
        pass

    def _release_texture(self, player):
        '''Release the player's texture.'''
        pass

class StreamingSource(Source):
    '''A source that is decoded as it is being played, and can only be
    queued once.
    '''
    
    _is_queued = False

    is_queued = property(lambda self: self._is_queued,
                         doc='''Determine if this source has been queued
        on a `Player` yet.

        Read-only.

        :type: bool
        ''')

class StaticSource(Source):
    '''A source that has been completely decoded in memory.  This source can
    be queued onto multiple players any number of times.
    '''
    
    def __init__(self, source):
        '''Construct a `StaticSource` for the data in `source`.

        :Parameters:
            `source` : `Source`
                The source to read and decode audio and video data from.

        '''


class BasePlayer(event.EventDispatcher):
    '''A sound and/or video player.

    Queue sources on this player to play them.
    '''

    #: The player will pause when it reaches the end of the stream.
    EOS_PAUSE = 'pause'
    #: The player will loop the current stream continuosly.
    EOS_LOOP = 'loop'
    #: The player will move on to the next queued stream when it reaches the
    #: end of the current source.  If there is no source queued, the player
    #: will pause.
    EOS_NEXT = 'next'

    # Source and queuing attributes
    _source = None
    _eos_action = EOS_NEXT
    _playing = False

    # Sound and spacialisation attributes
    _volume = 1.0
    _max_gain = 1.0
    _min_gain = 0.0

    _position = (0, 0, 0)
    _velocity = (0, 0, 0)
    _pitch = 1.0

    _cone_orientation = (0, 0, 0)
    _cone_inner_angle = 360.
    _cone_outer_angle = 360.
    _cone_outer_gain = 1.

    # Video attributes
    _texture = None

    def queue(self, source):
        '''Queue the source on this player.

        If the player has no source, the player will be paused immediately
        on this source.

        :Parameters:
            `source` : Source
                The source to queue.

        '''

    def play(self):
        '''Begin playing the current source.

        This has no effect if the player is already playing.
        '''
        raise NotImplementedError('abstract')

    def pause(self):
        '''Pause playback of the current source.

        This has no effect if the player is already paused.
        '''
        raise NotImplementedError('abstract')

    def seek(self, timestamp):
        '''Seek for playback to the indicated timestamp in seconds on the
        current source.  If the timestamp is outside the duration of the
        source, it will be clamped to the end.

        :Parameters:
            `timestamp` : float
                Timestamp to seek to.
        '''
        raise NotImplementedError('abstract')

    def next(self):
        '''Move immediately to the next queued source.

        If the `eos_action` of this player is `EOS_NEXT`, and the source has
        been queued for long enough, there will be no gap in the audio or
        video playback.  Otherwise, there may be some delay as the next source
        is prerolled and the first frames decoded and buffered.
        '''
        raise NotImplementedError('abstract')

    def dispatch_events(self):
        '''Dispatch any pending events and perform regular heartbeat functions
        to maintain playback.
        '''
        pass

    def _get_time(self):
        raise NotImplementedError('abstract')

    time = property(lambda self: self._get_time(),
                    doc='''Retrieve the current playback time of the current
         source.
                    
         The playback time is a float expressed in seconds, with 0.0 being
         the beginning of the sound.  The playback time returned represents
         the time encoded in the source, and may not reflect actual time
         passed due to pitch shifting or pausing.

         Read-only.

         :type: float
         ''')

    def _get_source(self):
        return self._source

    source = property(lambda self: self._get_source(),
                      doc='''Return the current source.

         Read-only.

         :type: Source
         ''')

    def _set_eos_action(self, action):
        self._eos_action = action

    eos_action = property(lambda self: self._eos_action,
                          _set_eos_action,
                          doc='''Set the behaviour of the player when it
        reaches the end of the current source.

        This must be one of the constants `EOS_NEXT`, `EOS_PAUSE` or
        `EOS_LOOP`.

        :type: str
        ''')

    playing = property(lambda self: self._playing,
                       doc='''Determine if the player state is playing.

        The `playing` property is irrespective of whether or not there is
        actually a source to play.  If `playing` is True and a source is
        queued, it will begin playing immediately.  If `playing` is False, 
        it is implied that the player is paused.  There is no other possible
        state.

        Read-only.

        :type: bool
        ''')

    def _set_volume(self, volume):
        raise NotImplementedError('abstract')

    volume = property(lambda self: self._volume,
                      lambda self, volume: self._set_volume(volume),
                      doc='''The volume level of sound playback.

         The nominal level is 1.0, and 0.0 is silence.

         The volume level is affected by factors such as the distance from the
         listener (if positioned), and is clamped (after distance attenuation)
         to the range [min_gain, max_gain].
         
         :type: float
         ''')

    def _set_min_gain(self, min_gain):
        raise NotImplementedError('abstract')

    min_gain = property(lambda self: self._min_gain,
                        lambda self, min_gain: self._set_min_gain(min_gain),
                        doc='''The minimum gain to apply to the sound, even

         The gain is clamped after distance attenuation.  The default value
         is 0.0.
         
         :type: float
         ''')

    def _set_max_gain(self, max_gain):
        raise NotImplementedError('abstract')

    max_gain = property(lambda self: self._max_gain,
                        lambda self, max_gain: self._set_max_gain(max_gain),
                        doc='''The maximum gain to apply to the sound.
         
         The gain is clamped after distance attenuation.  The default value
         is 1.0.
         
         :type: float
         ''')

    def _set_position(self, position):
        raise NotImplementedError('abstract')

    position = property(lambda self: self._position,
                        lambda self, position: self._set_position(position),
                        doc='''The position of the sound in 3D space.

        The position is given as a tuple of floats (x, y, z).  The unit
        defaults to meters, but can be modified with the listener
        properties.
        
        :type: 3-tuple of float
        ''')

    def _set_velocity(self, velocity):
        raise NotImplementedError('abstract')

    velocity = property(lambda self: self._velocity,
                        lambda self, velocity: self._set_velocity(velocity),
                        doc='''The velocity of the sound in 3D space.

        The velocity is given as a tuple of floats (x, y, z).  The unit
        defaults to meters per second, but can be modified with the listener
        properties.
        
        :type: 3-tuple of float
        ''')

    def _set_pitch(self, pitch):
        raise NotImplementedError('abstract')

    pitch = property(lambda self: self._pitch,
                     lambda self, pitch: self._set_pitch(pitch),
                     doc='''The pitch shift to apply to the sound.

        The nominal pitch is 1.0.  A pitch of 2.0 will sound one octave
        higher, and play twice as fast.  A pitch of 0.5 will sound one octave
        lower, and play twice as slow.  A pitch of 0.0 is not permitted.
        
        The pitch shift is applied to the source before doppler effects.
        
        :type: float
        ''')

    def _set_cone_orientation(self, cone_orientation):
        raise NotImplementedError('abstract')

    cone_orientation = property(lambda self: self._cone_orientation,
                                lambda self, c: self._set_cone_orientation(c),
                                doc='''The direction of the sound in 3D space.
                                
        The direction is specified as a tuple of floats (x, y, z), and has no
        unit.  The default direction is (0, 0, -1).  Directional effects are
        only noticeable if the other cone properties are changed from their
        default values.
        
        :type: 3-tuple of float
        ''')

    def _set_cone_inner_angle(self, cone_inner_angle):
        raise NotImplementedError('abstract')

    cone_inner_angle = property(lambda self: self._cone_inner_angle,
                                lambda self, a: self._set_cone_inner_angle(a),
                                doc='''The interior angle of the inner cone.
                                
        The angle is given in degrees, and defaults to 360.  When the listener
        is positioned within the volume defined by the inner cone, the sound
        is played at normal gain (see `volume`).
        
        :type: float
        ''')

    def _set_cone_outer_angle(self, cone_outer_angle):
        raise NotImplementedError('abstract')

    cone_outer_angle = property(lambda self: self._cone_outer_angle,
                                lambda self, a: self._set_cone_outer_angle(a),
                                doc='''The interior angle of the outer cone.
                                
        The angle is given in degrees, and defaults to 360.  When the listener
        is positioned within the volume defined by the outer cone, but outside
        the volume defined by the inner cone, the gain applied is a smooth
        interpolation between `volume` and `cone_outer_gain`.
        
        :type: float
        ''')

    def _set_cone_outer_gain(self, cone_outer_gain):
        raise NotImplementedError('abstract')

    cone_outer_gain = property(lambda self: self._cone_outer_gain,
                                lambda self, g: self._set_cone_outer_gain(g),
                                doc='''The gain applied outside the cone.
                                
        When the listener is positioned outside the volume defined by the
        outer cone, this gain is applied instead of `volume`.
        
        :type: float
        ''')

    texture = property(lambda self: self._texture,
                       doc='''The video texture.

        You should rerequest this property every time you display a frame
        of video, as multiple textures might be used.  This property will
        be `None` if there is no video in the current source.

        :type: `pyglet.image.Texture`
        ''')

    if getattr(sys, 'is_epydoc', False):
        def on_eos():
            '''The player has reached the end of the current source.

            This event is dispatched regardless of the EOS action.  You
            can alter the EOS action in this event handler, however playback
            may stutter as the media device will not have enough time to
            decode and buffer the new data in advance.

            :event:
            '''
BasePlayer.register_event_type('on_eos')

class Listener(object):
    '''The listener properties for positional audio.

    You can obtain the singleton instance of this class as
    `pyglet.media.listener`.
    '''
    _volume = 1.0
    _position = (0, 0, 0)
    _velocity = (0, 0, 0)
    _forward_orientation = (0, 0, -1)
    _up_orientation = (0, 1, 0)

    _doppler_factor = 1.
    _speed_of_sound = 343.3

    def _set_volume(self, volume):
        raise NotImplementedError('abstract')

    volume = property(lambda self: self._volume,
                      lambda self, volume: self._set_volume(volume),
                      doc='''The master volume for sound playback.

        All sound volumes are multiplied by this master volume before being
        played.  A value of 0 will silence playback (but still consume
        resources).  The nominal volume is 1.0.
        
        :type: float
        ''')

    def _set_position(self, position):
        raise NotImplementedError('abstract')

    position = property(lambda self: self._position,
                        lambda self, position: self._set_position(position),
                        doc='''The position of the listener in 3D space.

        The position is given as a tuple of floats (x, y, z).  The unit
        defaults to meters, but can be modified with the listener
        properties.
        
        :type: 3-tuple of float
        ''')

    def _set_velocity(self, velocity):
        raise NotImplementedError('abstract')

    velocity = property(lambda self: self._velocity,
                        lambda self, velocity: self._set_velocity(velocity),
                        doc='''The velocity of the listener in 3D space.

        The velocity is given as a tuple of floats (x, y, z).  The unit
        defaults to meters per second, but can be modified with the listener
        properties.
        
        :type: 3-tuple of float
        ''')

    def _set_forward_orientation(self, orientation):
        raise NotImplementedError('abstract')

    forward_orientation = property(lambda self: self._forward_orientation,
                               lambda self, o: self._set_forward_orientation(o),
                               doc='''A vector giving the direction the
        listener is facing.

        The orientation is given as a tuple of floats (x, y, z), and has
        no unit.  The forward orientation should be orthagonal to the
        up orientation.
        
        :type: 3-tuple of float
        ''')

    def _set_up_orientation(self, orientation):
        raise NotImplementedError('abstract')

    up_orientation = property(lambda self: self._up_orientation,
                              lambda self, o: self._set_up_orientation(o),
                              doc='''A vector giving the "up" orientation
        of the listener.

        The orientation is given as a tuple of floats (x, y, z), and has
        no unit.  The up orientation should be orthagonal to the
        forward orientation.
        
        :type: 3-tuple of float
        ''')

    def _set_doppler_factor(self, factor):
        raise NotImplementedError('abstract')

    doppler_factor = property(lambda self: self._doppler_factor,
                              lambda self, f: self._set_doppler_factor(f),
                              doc='''The emphasis to apply to the doppler
        effect for sounds that move relative to the listener.

        The default value is 1.0, which results in a physically-based
        calculation.  The effect can be enhanced by using a higher factor,
        or subdued using a fractional factor (negative factors are
        ignored).
        
        :type: float
        ''')

    def _set_speed_of_sound(self, speed_of_sound):
        raise NotImplementedError('abstract')

    speed_of_sound = property(lambda self: self._speed_of_sound,
                              lambda self, s: self._set_speed_of_sound(s),
                              doc='''The speed of sound, in units per second.

        The default value is 343.3, a typical result at sea-level on a mild
        day, using meters as the distance unit.

        The speed of sound only affects the calculation of pitch shift to 
        apply due to doppler effects; in particular, no propogation delay
        or relative phase adjustment is applied (in current implementations
        of audio devices).

        :type: float
        ''')

if getattr(sys, 'is_epydoc', False):
    #: The singleton listener.
    #:
    #: :type: `Listener`
    listener = Listener()

    # Document imaginary Player class
    Player = BasePlayer
    Player.__name__ = 'Player'
    del BasePlayer

    # Document imaginary ManagedSoundPlayer class.  There is no point making
    # a BaseManagedSoundPlayer class; it won't fit into the devices' class
    # hierarchies.
    class ManagedSoundPlayer(Player):
        '''A player which takes care of updating its own audio buffers.

        This player will continue playing the sound until the sound is
        finished, even if the application discards the player early.
        There is no need to call `Player.dispatch_events` on this player,
        though you must call `pyglet.media.dispatch_events`.
        '''

        #: The only possible end of stream action for a managed player.
        EOS_STOP = 'stop'

        eos_action = property(lambda self: EOS_STOP,
                              doc='''The fixed eos_action is `EOS_STOP`,
            in which the player is discarded as soon as the source has
            finished.

            Read-only.
            
            :type: str
            ''')
                              

    def load(filename, file=None, streaming=True):
        '''Load a source.

        :Parameters:
            `filename` : str
                Filename to load.
            `file` : file-like object
                File to load data from.  If unspecified, the filename will be
                opened.
            `streaming` : bool
                If unspecified, the source returned will be streaming, and can
                only be used once.  Specify `False` here to return a
                fully decoded `StaticSource`.

        :rtype: `Source`
        '''

    def dispatch_events():
        '''Process managed audio events.

        You must call this function regularly (typically once per run loop
        iteration) in order to keep audio buffers of managed players full.
        '''

else:
    # Currently audio playback is through OpenAL on all platforms; in 
    # the future alternative drivers using ALSA or DirectSound may be
    # implemented.
    from pyglet.media import openal
    openal.init()
    Player = openal.OpenALPlayer
    '''
    if sys.platform == 'linux2':
        from pyglet.media import gst_openal
        _device = gst_openal
    elif sys.platform == 'darwin':
        from pyglet.media import quicktime
        _device = quicktime
    elif sys.platform in ('win32', 'cygwin'):
        from pyglet.media import directshow
        _device = directshow
    else:
        raise ImportError('pyglet.media not yet supported on %s' % sys.platform)

    load = _device.load
    Player = _device.Player
    ManagedSoundPlayer = _device.ManagedSoundPlayer
    dispatch_events = _device.dispatch_events
    listener = _device.listener
    _device.init()
    '''
