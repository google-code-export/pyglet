#!/usr/bin/python
# $Id:$

from pyglet.media import Source, CannotSeekException
from pyglet.media.openal import buffer_pool
from pyglet.media import lib_openal as al

import ctypes
import os
import math

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
        if bytes_per_sample == 1:
            return '\127' * bytes
        else:
            return '\0' * bytes

class WhiteNoise(ProceduralSource):
    def _get_data(self, bytes, sample_rate, bytes_per_sample):
        return os.urandom(bytes)

class Sine(ProceduralSource):
    def __init__(self, duration, frequency=440, **kwargs):
        super(Sine, self).__init__(duration, **kwargs)
        self.frequency = frequency
        
    def _get_data(self, bytes, sample_rate, bytes_per_sample):
        if bytes_per_sample == 1:
            samples = bytes
            bias = 127
            amplitude = 127
            data = (ctypes.c_ubyte * samples)()
        else:
            samples = bytes >> 1
            bias = 0
            amplitude = 32767
            data = (ctypes.c_short * samples)()
        step = self.frequency * (math.pi * 2) / sample_rate
        for i in range(samples):
            data[i] = int(math.sin(step * i) * amplitude + bias)
        return data

class Saw(ProceduralSource):
    def __init__(self, duration, frequency=440, **kwargs):
        super(Saw, self).__init__(duration, **kwargs)
        self.frequency = frequency
        
    def _get_data(self, bytes, sample_rate, bytes_per_sample):
        if bytes_per_sample == 1:
            samples = bytes
            value = 127
            max = 255
            min = 0
            data = (ctypes.c_ubyte * samples)()
        else:
            samples = bytes >> 1
            value = 0
            max = 32767
            min = -32768
            data = (ctypes.c_short * samples)()
        step = (max - min) * 2 * self.frequency / sample_rate
        for i in range(samples):
            value += step
            if value > max:
                value = max - (value - max)
                step = -step
            if value < min:
                value = min - (value - min)
                step = -step
            data[i] = value
        return data

class Square(ProceduralSource):
    def __init__(self, duration, frequency=440, **kwargs):
        super(Square, self).__init__(duration, **kwargs)
        self.frequency = frequency
        
    def _get_data(self, bytes, sample_rate, bytes_per_sample):
        if bytes_per_sample == 1:
            samples = bytes
            value = 0
            amplitude = 255
            data = (ctypes.c_ubyte * samples)()
        else:
            samples = bytes >> 1
            value = -32768
            amplitude = 65535
            data = (ctypes.c_short * samples)()
        period = sample_rate / self.frequency / 2
        count = 0
        for i in range(samples):
            count += 1
            if count == period:
                value = amplitude - value
                count = 0
            data[i] = value
        return data


