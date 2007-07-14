#!/usr/bin/python
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2007 Alex Holkner
# All rights reserved.
# 
# Redistribution and use in _al_source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  * Redistributions of _al_source code must retain the above copyright
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

import ctypes
import sys
import time

from pyglet.media import BasePlayer, Listener, MediaException
from pyglet.media import lib_openal as al
from pyglet.media import lib_alc as alc

_device = None
_is_init = False
_have_1_1 = False
def init(device_name = None):
    global _device
    global _is_init
    global _have_1_1

    # TODO devices must be enumerated on Windows, otherwise 1.0 context is
    # returned.

    _device = alc.alcOpenDevice(device_name)
    if not _device:
        raise Exception('No OpenAL device.')

    alcontext = alc.alcCreateContext(_device, None)
    alc.alcMakeContextCurrent(alcontext)
    _is_init = True

    if have_version(1, 1):
        # Good version info to cache
        _have_1_1 = True

def _split_nul_strings(s):
    # NUL-separated list of strings, double-NUL-terminated.
    nul = False
    i = 0
    while True:
        if s[i] == '\0':
            if nul:
                break
            else:
                nul = True
        else:
            nul = False
        i += 1
    s = s[:i - 1]
    return s.split('\0')

def get_version():
    major = alc.ALCint()
    minor = alc.ALCint()
    alc.alcGetIntegerv(_device, alc.ALC_MAJOR_VERSION, 
                       ctypes.sizeof(major), major)
    alc.alcGetIntegerv(_device, alc.ALC_MINOR_VERSION, 
                       ctypes.sizeof(minor), minor)
    return major.value, minor.value

def have_version(major, minor):
    return (major, minor) <= get_version()

def get_extensions():
    extensions = alc.alcGetString(_device, alc.ALC_EXTENSIONS)
    if sys.platform == 'darwin':
        return ctypes.cast(extensions, ctypes.c_char_p).value.split(' ')
    else:
        return _split_nul_strings(extensions)

def have_extension(extension):
    return extension in get_extensions()

class BufferInformation(object):
    __slots__ = ['timestamp', 'length', 'owner', 'is_eos']

class BufferPool(list):
    def __init__(self):
        self.info = {}

    def get(self, timestamp, length, owner, is_eos=False):
        if not self:
            buffer = al.ALuint()
            al.alGenBuffers(1, buffer)
            info = BufferInformation()
            self.info[buffer.value] = info
        else:
            buffer = al.ALuint(self.pop(0))
            info = self.info[buffer.value]
        info.timestamp = timestamp  # for video sync
        info.length = length        # in seconds
        info.owner = owner          # Source that owns it, or buffer_pool
        info.is_eos = is_eos        # True if last buffer for this source
        return buffer

    def info(self, buffer):
        return self.info[buffer]

    def release(self, buffer):
        '''Players should call this method when a buffer is finished
        playing.'''
        self.info[buffer].owner._openal_release_buffer(buffer)

    def _openal_release_buffer(self, buffer):
        '''Release a buffer.  Sources can set the buffer owner to be the
        buffer pool if the buffer can be released as soon it is played.
        '''
        self.append(buffer)

    def __del__(self, al=al):
        if al and al.ALuint and al.alDeleteBuffers:
            buffers = (al.ALuint * len(self))(*self)
            al.alDeleteBuffers(len(self), buffers)

buffer_pool = BufferPool()

_format_map = {
    (1,  8): al.AL_FORMAT_MONO8,
    (1, 16): al.AL_FORMAT_MONO16,
    (2,  8): al.AL_FORMAT_STEREO8,
    (2, 16): al.AL_FORMAT_STEREO16,
}
def get_format(channels, depth):
    return _format_map[channels, depth]

class SourceInfo(object):
    def __init__(self, source):
        self.source = source

class OpenALPlayer(BasePlayer):
    #: Seconds ahead to buffer audio
    _min_buffer_time = .5

    def __init__(self):
        super(OpenALPlayer, self).__init__()

        self._al_source = al.ALuint()
        al.alGenSources(1, self._al_source)
        # OpenAL on Linux lacks the time functions, so this is a stab at
        # interpolating time between the known buffer timestamps.  When a
        # timestamp is read from the active buffer, the current system time is
        # stored in self._last_buffer_time, and the buffer that was used is
        # stored in self._last_buffer. 
        #
        # If the same buffer is in use the next time the time is requested,
        # the elapsed system time is added to the buffer timestamp.
        #
        # The (completely invalid) assumption is that the buffer is just
        # beginning when _last_buffer_time is stored.  This is more likely
        # than not, at least, if the buffers are long.  If the buffers are
        # short, hopefully not much interpolation will be needed and the
        # difference won't be noticeable.
        #
        # The alternative -- reusing the same timestamp without adding system
        # time -- results in slightly jumpy video due to lost frames.
        #
        # When OpenAL 1.1 is present (i.e., on OS X), we add the buffer's
        # timestamp to the retrieved sample offset within the current buffer.
        self._last_buffer = -1
        self._last_known_timestamp = 0
        self._last_known_system_time = 0

        self._sources = []

        # Index into self._sources that is currently the source of new audio
        # buffers
        self._source_read_index = 0

        # List of BufferInformation
        self._queued_buffers = []

        # If not playing, must be paused (irrespective of whether or not
        # sources are queued).
        self._playing = False

        # self._al_playing = (_al_source.state == AL_PLAYING)
        self._al_playing = False

    def __del__(self, al=al):
        if al and al.alDeleteSources:
            al.alDeleteSources(1, self._al_source)

    def queue(self, source):
        if not self._sources:
            self._source_read_index = 0
            source._init_texture(self)
        self._sources.append(source)

    def next(self):
        if self._sources:
            old_source = self._sources.pop(0)
            old_source._release_texture(self)
            old_source._stop()
            self._source_read_index -= 1

        if self._sources:
            self._sources[0]._init_texture(self)
            
    def dispatch_events(self):
        if not self._sources or not self._playing:
            return

        # Calculate once only for this method.
        self_time = self.time
        
        if self._sources[0].has_audio:
            # Find out how many buffers are done
            processed = al.ALint()
            al.alGetSourcei(self._al_source, 
                            al.AL_BUFFERS_PROCESSED, processed)
            processed = processed.value

            # Release spent buffers
            if processed:
                buffers = (al.ALuint * processed)()
                al.alSourceUnqueueBuffers(self._al_source, 
                                          len(buffers), buffers)

                # If any buffers were EOS buffers, dispatch appropriate
                # event.
                for buffer in buffers:
                    info = self._queued_buffers.pop(0)
                    assert info is buffer_pool.info[buffer]
                    if info.is_eos:
                        if self._eos_action == self.EOS_NEXT:
                            self.next()
                        self.dispatch_event('on_eos')
                    buffer_pool.release(buffer)
        else:
            # Check for EOS on silent source
            if self_time > self._sources[0].duration:
                if self._eos_action == self.EOS_NEXT:
                    self.next()
                self.dispatch_event('on_eos')

        # Determine minimum duration of audio already buffered (current buffer
        # is ignored, as this could be just about to be dequeued).
        buffer_time = sum([b.length for b in self._queued_buffers[1:]])

        # Ensure audio buffers are full
        try:
            source = self._sources[self._source_read_index]
        except IndexError:
            source = None
        while source and buffer_time < self._min_buffer_time:
            if source.has_audio:
                buffer = source._openal_get_buffer()
            if source.has_audio and buffer is not None:
                info = buffer_pool.info[buffer.value]
                self._queued_buffers.append(info)
                buffer_time += info.length

                # Queue this buffer onto the AL source.
                al.alSourceQueueBuffers(self._al_source, 1, 
                                        ctypes.byref(buffer))
                
                # Start OpenAL playing if this player is playing, and if
                # this source that we're buffering is the current source
                # (i.e., not some noisy source queued after a silent source).
                if (self._playing and 
                    not self._al_playing and
                    self._source_read_index == 0):
                    al.alSourcePlay(self._al_source)
                    self._al_playing = True
            else:
                # No more buffers from source, check eos behaviour
                if self._eos_action == self.EOS_NEXT:
                    self._source_read_index += 1
                    try:
                        source = self._sources[self._source_read_index]
                        source._play() # Preroll source ahead of buffering
                    except IndexError:
                        source = None
                elif self._eos_action == self.EOS_LOOP:
                    source._seek(0)
                elif self._eos_action == self.EOS_PAUSE:
                    source = None
                else:
                    assert False, 'Invalid eos_action'

        # Update video texture
        if self._texture:
            self._sources[0]._update_texture(self, self_time)

    def _get_time(self):
        if not self._sources:
            return 0.0
        
        if self._sources[0].has_audio:
            # Add current buffer timestamp to sample offset within that
            # buffer.
            buffer = al.ALint()
            al.alGetSourcei(self._al_source, al.AL_BUFFER, buffer)
            if not buffer or not al.alIsBuffer(buffer.value):
                return 0.0

            # The playback position at the start of the current buffer
            buffer_timestamp = buffer_pool.info[buffer.value].timestamp

            if _have_1_1:
                # Add buffer timestamp to sample offset
                buffer_samples = al.ALint()
                al.alGetSourcei(self._al_source, 
                                al.AL_SAMPLE_OFFSET, buffer_samples)
                sample_rate = al.ALint()
                al.alGetBufferi(buffer.value, al.AL_FREQUENCY, sample_rate)
                buffer_time = buffer_samples.value / float(sample_rate.value)
                return buffer_timestamp + buffer_time
            else:
                if not self._playing:
                    # Paused.
                    return self._last_known_timestamp
                elif buffer.value == self._last_buffer:
                    # Interpolate system time past buffer timestamp
                    return (time.time() - self._last_known_system_time + 
                            self._last_known_timestamp)
                else:
                    # Buffer has changed, assume we are at the start of it.
                    self._last_known_system_time = time.time()
                    self._last_known_timestamp = buffer_timestamp
                    self._last_buffer = buffer.value
                    return buffer_timestamp
        else:
            # There is no audio data, so we use system time to track the 
            # timestamp.
            return (time.time() - self._last_known_system_time +
                    self._last_known_timestamp)


    def play(self):
        if self._playing:
            return

        self._playing = True

        if not self._sources:
            return

        if self._sources[0].has_audio:
            buffers = al.ALint()
            al.alGetSourcei(self._al_source, al.AL_BUFFERS_QUEUED, buffers)
            if buffers.value:
                al.alSourcePlay(self._al_source)
                self._al_playing = True
        self._last_known_system_time = time.time()
        self._last_known_timestamp = time.time() - self._last_known_timestamp

    def pause(self):
        self._playing = False

        if not self._sources:
            return

        if self._al_playing:
            al.alSourcePause(self._al_source)
            self._al_playing = False

    def seek(self, timestamp):
        if self._sources:
            self._sources[0]._seek(timestamp)
            self._last_known_system_time = time.time()
            self._last_known_timestamp = timestamp

    def _get_source(self):
        if self._sources:
            return self._sources[0]
        return None

    def _set_volume(self, volume):
        al.alSourcef(self._al_source, al.AL_GAIN, max(0, volume))
        self._volume = volume

    def _set_min_gain(self, min_gain):
        al.alSourcef(self._al_source, al.AL_MIN_GAIN, max(0, min_gain))
        self._min_gain = min_gain

    def _set_max_gain(self, max_gain):
        al.alSourcef(self._al_source, al.AL_MAX_GAIN, max(0, max_gain))
        self._max_gain = max_gain

    def _set_position(self, position):
        x, y, z = position
        al.alSource3f(self._al_source, al.AL_POSITION, x, y, z)
        self._position = position

    def _set_velocity(self, velocity):
        x, y, z = velocity
        al.alSource3f(self._al_source, al.AL_VELOCITY, x, y, z)
        self._velocity = velocity

    def _set_pitch(self, pitch):
        al.alSourcef(self._al_source, al.AL_PITCH, max(0, pitch))
        self._pitch = pitch

    def _set_cone_orientation(self, cone_orientation):
        x, y, z = cone_orientation
        al.alSource3f(self._al_source, al.AL_DIRECTION, x, y, z)
        self._cone_orientation = cone_orientation

    def _set_cone_inner_angle(self, cone_inner_angle):
        al.alSourcef(self._al_source, al.AL_CONE_INNER_ANGLE, cone_inner_angle)
        self._cone_inner_angle = cone_inner_angle

    def _set_cone_outer_angle(self, cone_outer_angle):
        al.alSourcef(self._al_source, al.AL_CONE_OUTER_ANGLE, cone_outer_angle)
        self._cone_outer_angle = cone_outer_angle

    def _set_cone_outer_gain(self, cone_outer_gain):
        al.alSourcef(self._al_source, al.AL_CONE_OUTER_GAIN, cone_outer_gain)
        self._cone_outer_gain = cone_outer_gain


'''
class OpenALStreamingSound(OpenALSound):
    def __del__(self):
        try:
            self.stop()
        except (ValueError, TypeError, NameError):
            # we're being __del__'ed during interpreter exit
            # (ValueError would come from trying to unschedule us from the
            # event instances list, NameError from trying to use already-
            # collected modules and TypeError from trying to invoke methods
            # on collected objects)
            pass

    def stop(self):
        super(OpenALStreamingSound, self).stop()

        # Release all buffers
        queued = al.ALint()
        al.alGetSourcei(self._al_source, al.AL_BUFFERS_QUEUED, queued)
        self._release_buffers(queued.value)

    def dispatch_events(self):
        super(OpenALStreamingSound, self).dispatch_events()

        # Release spent buffers
        if self._processed_buffers:
            self._release_buffers(self._processed_buffers)

    def _release_buffers(self, num_buffers):
        discard_buffers = (al.ALuint * num_buffers)()
        al.alSourceUnqueueBuffers(
            self._al_source, len(discard_buffers), discard_buffers)
        buffer_pool.replace(discard_buffers)


class OpenALStaticSound(OpenALSound):
    def __init__(self, medium):
        super(OpenALStaticSound, self).__init__()

        # Keep a reference to the medium to avoid premature release of
        # buffers.
        self.medium = medium

    def stop(self):
        super(OpenALSound, self).stop()

        self.medium = None
'''

class OpenALListener(Listener):
    def _set_position(self, position):
        x, y, z = position
        al.alListener3f(al.AL_POSITION, x, y, z)
        self._position = position 

    def _set_velocity(self, velocity):
        x, y, z = velocity
        al.alListener3f(al.AL_VELOCITY, x, y, z)
        self._velocity = velocity 

    def _set_forward_orientation(self, orientation):
        val = (ALfloat * 6)(*(orientation + self._up_orientation))
        al.alListenerfv(al.AL_ORIENTATION, val)
        self._forward_orientation = orientation

    def _set_up_orientation(self, orientation):
        val = (ALfloat * 6)(*(self._forward_orientation + orientation))
        al.alListenerfv(al.AL_ORIENTATION, val)
        self._up_orientation = orientation

    def _set_doppler_factor(self, factor):
        al.alDopplerFactor(factor)
        self._doppler_factor = factor

    def _set_speed_of_sound(self, speed_of_sound):
        al.alSpeedOfSound(speed_of_sound)
        self._speed_of_sound = speed_of_sound
