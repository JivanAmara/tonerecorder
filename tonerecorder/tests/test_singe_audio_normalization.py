'''
Created on Jul 11, 2016

@author: jivan
'''
import os
import pytest
from tonerecorder.normalize_samples import convert_wav, normalize_volume, strip_silence


def test_normalization_pipeline():
    test_audio_dir = os.path.normpath(os.path.dirname(__file__))
    test_audio_filename = 'test_audio.mp3'
    test_audio_path = os.path.join(test_audio_dir, test_audio_filename)

    test_output_dir = '/tmp'
    filename_base = '.'.join(test_audio_filename.split('.')[:-1])

    cw_filename = filename_base + '.convert.wav'
    nv_filename = filename_base + '.normalize_volume.wav'
    ss_filename = filename_base + '.strip_silence.wav'

    cw_filepath = os.path.join(test_output_dir, cw_filename)
    convert_wav(test_audio_path, cw_filepath)
    assert(os.path.exists(cw_filepath))

    nv_filepath = os.path.join(test_output_dir, nv_filename)
    normalize_volume(cw_filepath, nv_filepath)
    assert(os.path.exists(nv_filepath))
    os.unlink(cw_filepath)

    ss_filepath = os.path.join(test_output_dir, ss_filename)
    strip_silence(nv_filepath, ss_filepath)
    assert(os.path.exists(ss_filepath))
    os.unlink(nv_filepath)

    os.unlink(ss_filepath)

