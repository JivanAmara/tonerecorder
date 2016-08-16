'''
Created on Apr 21, 2016

@author: jivan
'''
from __future__ import print_function

import argparse
try:
    import cStringIO as StringIO
except:
    from io import StringIO
import hashlib
import logging
import os, sys
import shutil
import sndhdr
from subprocess import Popen
import subprocess
from tempfile import NamedTemporaryFile
from time import sleep
from uuid import uuid1
from ttlib.normalization.interface import convert_wav, normalize_volume, strip_silence

import taglib

import django
# from guppy import hpy
import mutagen.mp3
import resource  # @UnresolvedImport

logger = logging.getLogger(__name__)

NORMALIZE_VERSION = '0.1'

def normalize_all():
    print('Converting original audio to standardized wav.')
    convert_wav_all()
    print('Normalizing volume of wav.')
    normalize_volume_all()
    print('Stripping silence from wav.')
    strip_silence_all()

# --- Hack sndhdr to accept StringIO objects
def whathdr_stringio(sio):
    """Recognize sound headers -- accepts StringIO instead of filename as sndhdr.whathdr()"""
    h = sio.read(512)
    for tf in sndhdr.tests:
        res = tf(h, sio)
        if res:
            return res
    return None
sndhdr.whathdr_stringio = whathdr_stringio

def get_metadata(rs):
    """ Returns the file extension, sample rate, and audio length for the .content
        property of the RecordedSyllable passed.
    """
    logger.info(
        'get_metadata() for rs w/ id ({}), file extension: {}'.format(rs.id, rs.file_extension)
    )
    sys.stdout.flush()
    # In-Memory 'file'
    f = StringIO.StringIO(rs.content)
    audio_details = sndhdr.whathdr_stringio(f)

    if audio_details:
        (type, sample_rate, channels, frames, bits_per_sample) = audio_details
        audio_metadata = (rs.file_extension, sample_rate, None)
    else:
        ntf = NamedTemporaryFile(suffix='.{}'.format(rs.file_extension))
        ntf.write(rs.content)
        ntf.seek(0)

        try:
            tlinfo = taglib.File(ntf.name)
            sample_rate = tlinfo.sampleRate
            try:
#             if rs.file_extension not in ['amr', 'wma']:
                audio = mutagen.mp3.MP3(ntf.name)
                audio_length = audio.info.length
            except mutagen.mp3.HeaderNotFoundError:
#             else:
                audio_length = None
            audio_metadata = (rs.file_extension, sample_rate, audio_length)
        finally:
            ntf.close()

    return audio_metadata

def get_file_metadata(filepath):
    """ *brief*: Returns the file extension, sample rate, and audio length for the audio file located at
            *filepath*.
    """
    try:
        file_extension = filepath.split('.')[:-1]
    except IndexError:
        file_extension = None

    with open(filepath, 'rb') as f:
        audio_details = sndhdr.whathdr_stringio(f)

    if audio_details:
        (type, sample_rate, channels, frames, bits_per_sample) = audio_details
        audio_metadata = (file_extension, sample_rate, None)
    else:
        tlinfo = taglib.File(filepath)
        sample_rate = tlinfo.sampleRate
        try:
            audio = mutagen.mp3.MP3(filepath)
            audio_length = audio.info.length
        except mutagen.mp3.HeaderNotFoundError:
            audio_length = None
        audio_metadata = (file_extension, sample_rate, audio_length)

    return audio_metadata

def convert_wav_all():
    nrecs = RecordedSyllable.objects.count()
    print('Converting {} Samples to wav format w/ standard sample rate of 14400'.format(nrecs))
    print('x No audio_original or file missing')
    print('X Error processing entry')
    print('o Already normalized')
    print('. Normalizing')

    for rs in RecordedSyllable.objects.all().select_related('user', 'syllable'):
        if rs.audio_original is None or not os.path.exists(rs.audio_original):
            print('x', end='')
            sys.stdout.flush()
            continue

        if (rs.audio_original and rs.normalize_version == NORMALIZE_VERSION
             and os.path.exists(rs.audio_wav)):
            print('o', end='')
            sys.stdout.flush()
            continue

        wavfilename = rs.create_audio_path('wav')
        try:
            convert_wav(rs.audio_original, wavfilename)
        except:
            print('X', end='')
            continue

        rs.audio_wav = wavfilename
        rs.normalize_version = NORMALIZE_VERSION
        rs.save()
        print('.', end='')
        sys.stdout.flush()
    print()

def normalize_volume_all(remove_files=True):
    nrecs = RecordedSyllable.objects.count()
    print('Normalizing Volume for {} Samples'.format(nrecs))

    print('. Making normalized version')
    print('o Normalized version already exists')
    print('- Normalized version matches original')
    print('x No audio_wav')
    # Break the RecordedSyllable retrieval up into chunks to limit memory usage.
    qschunksize = 500
    qschunks = [
        RecordedSyllable.objects\
            .select_related('user', 'syllable')[i:i + qschunksize]
            for i in range(0, nrecs - qschunksize, qschunksize)
    ]
    for qschunk in qschunks:
        for rs in qschunk:
            if (rs.audio_normalized_volume
                and rs.normalize_version == NORMALIZE_VERSION
                and os.path.exists(rs.audio_normalized_volume)
            ):
                print('o', end='')
                sys.stdout.flush()
                continue

            if not rs.audio_wav or not os.path.exists(rs.audio_wav):
                print('x', end='')
                sys.stdout.flush()
                continue
            rs.audio_normalized_volume = None

            normalized_filepath = rs.create_audio_path('volume_normalized')
            normalize_volume(rs.audio_wav, normalized_filepath)

            hash1 = hashlib.sha224(open(rs.audio_wav, 'rb').read()).hexdigest()
            rs.audio_normalized_volume = normalized_filepath
            rs.normalize_version = NORMALIZE_VERSION
            rs.save()

            hash2 = hashlib.sha224(open(rs.audio_normalized_volume, 'rb').read()).hexdigest()
            if hash1 == hash2:
                print('-', end='')
            else:
                print('.', end='')
                sys.stdout.flush()
    print()

def strip_silence_all():
    ''' Copies RecordedSyllable.content_as_normalized_wav to
            RecordedSyllable.content_as_silence_stripped_wav with preceding & trailing silence
            removed.
    '''
    rs_count = RecordedSyllable.objects.count()
    print('Stripping silence from {} RecordedSyllable objects'.format(rs_count))
    print('. Stripped silence')
    print('o Silence already stripped, ignoring')
    print('x No audio_normalized_volume')
    print('X Error stripping silence')
    rschunksize = 1000
    for chunkstart in range(0, rs_count - rschunksize, rschunksize):
#         print('Memory usage before chunk[{}:{}]: {}'\
#               .format(
#                   chunkstart, chunkstart + rschunksize,
#                   resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
#         )
        rschunk = RecordedSyllable.objects\
            .select_related('user', 'syllable')[chunkstart:chunkstart + rschunksize].iterator()

#         hp = hpy()
#         before = hp.heap()
#         leftovers = []
        for rs in rschunk:
            if (rs.audio_silence_stripped is not None
                and rs.normalize_version == NORMALIZE_VERSION
                and os.path.exists(rs.audio_silence_stripped)
            ):
                print('o', end='')
                sys.stdout.flush()
                continue

            if rs.audio_normalized_volume is None or not os.path.exists(rs.audio_normalized_volume):
                print('x', end='')
                sys.stdout.flush()
                continue

            stripped_filepath = rs.create_audio_path('silence_stripped')
            try:
                strip_silence(rs.audio_normalized_volume, stripped_filepath)
            except:
                print('X', end='')
                sys.stdout.flush()
                continue

            rs.audio_silence_stripped = stripped_filepath
            rs.normalize_version = NORMALIZE_VERSION
#             leftovers.append(hp.heap() - before)
            rs.save()
#             leftovers.append(hp.heap() - before)
            print('.', end='')
            sys.stdout.flush()
#         print('Memory usage after chunk[{}:{}]: {}'\
#               .format(
#                   chunkstart, chunkstart + rschunksize,
#                   resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
#         )
#         for i, leftover in enumerate(leftovers):
#             print('Heap diff{}:\n{}'.format(i, leftover))


# Full path to the directory containing this file.
DIRPATH = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # --- makewav
    makewav_parser = subparsers.add_parser(
        'makewav', help='Converts RecordedSyllable original audio to to 44100Hz wav format.')
    makewav_parser.set_defaults(subcommand='makewav')

    # --- normalize_volume
    normalize_volume_parser = subparsers.add_parser(
        'normalize_volume', help='Normalize the audio volume for all samples'
    )
    normalize_volume_parser.set_defaults(subcommand='normalize_volume')

    # --- stripsilence
    stripsilence_parser = subparsers.add_parser(
        'stripsilence', help='Remove preceding/following silence for all samples'
    )
    stripsilence_parser.set_defaults(subcommand='stripsilence')

    # --- normalize (all)
    normalize_parser = subparsers.add_parser(
        'normalize', help='Execute all of the normalization procedures for all samples'
    )
    normalize_parser.set_defaults(subcommand='normalize')

    args = parser.parse_args()

    sys.path.append(DIRPATH)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'script_settings'
    django.setup()
    from django.conf import settings

    from hanzi_basics.models import PinyinSyllable
    from tonerecorder.models import RecordedSyllable
    from django.contrib.auth.models import User

    if not hasattr(args, 'subcommand'):
        print('You must provide a subcommand.  Run with -h to see options.')
    elif args.subcommand == 'makewav':
        convert_wav_all()
    elif args.subcommand == 'normalize_volume':
        normalize_volume_all()
    elif args.subcommand == 'stripsilence':
        strip_silence_all(recalculate=args.recalc)
    elif args.subcommand == 'normalize':
        normalize_all()
    else:
        raise Exception('Unexpected subcommand {}'.format(args.subcommand))
