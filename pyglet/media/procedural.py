#!/usr/bin/python
# $Id:$

from pyglet.media import Source, CannotSeekException
from pyglet.media.openal import buffer_pool
from pyglet.media import lib_openal as al

import os

class ProceduralSource(Source):
    has_audio = True
    
    def __init__(self, duration, sample_rate=44800, sample_size=16):
        self._duration = float(duration)
        self.audio_properties = {'sample_rate': int(sample_rate),
                                 'sample_size': int(sample_size),}

        self._played = False

    def _get_data(self, bytes, sample_rate, bytes_per_sample):
        raise NotImplementedError('abstract')

    def _openal_get_buffer(self):
        if self._played:
            return None, None
        sample_rate = self.audio_properties['sample_rate']
        sample_size = self.audio_properties['sample_size']
        bytes_per_sample = sample_size >> 3
        format = {
            8: al.AL_FORMAT_MONO8,
            16: al.AL_FORMAT_MONO16,
        }[sample_size]
        bytes = int(bytes_per_sample * self._duration * sample_rate)
        data = self._get_data(bytes, sample_rate, bytes_per_sample)
        buffer = buffer_pool.get(0, self._duration)
        al.alBufferData(buffer, format, data, bytes, sample_rate)

        self._played = True
        return buffer, self._duration

    def _seek(self, timestamp):
        if timestamp == 0:
            self._played = False
        else:
            raise CannotSeekException()

class Silence(ProceduralSource):
    def _get_data(self, bytes, sample_rate, bytes_per_sample):
        return '\0' * bytes

class WhiteNoise(ProceduralSource):
    def _get_data(self, bytes, sample_rate, bytes_per_sample):
        return os.urandom(bytes)
