'''
Created on Apr 21, 2016

@author: jivan
'''
from __future__ import print_function

import argparse
import cStringIO
import hashlib
import os, sys
import re
import sndhdr
from subprocess import Popen
import subprocess
from tempfile import NamedTemporaryFile
from time import sleep
from uuid import uuid1
import scipy.io.wavfile
import numpy
import django
import mutagen.mp3
import taglib
from tonerecorder.models import RecordedSyllable
import logging

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


def convert_wav_all(remove_files=True):
    print('Process {} remove intermediary files.'.format('will' if remove_files else 'will not'))
    nrecs = RecordedSyllable.objects.filter(recording_ok=True).count()
    print('Converting {} Samples to wav format w/ standard sample rate of 14400'.format(nrecs))

    for rs in RecordedSyllable.objects.all().filter(recording_ok=True).select_related('user', 'syllable'):
        if rs.content_as_wav and rs.normalize_version == NORMALIZE_VERSION:
            print('o', end='')
            sys.stdout.flush()
            continue

        try:
            extension, sample_rate, audio_length = get_metadata(rs)
        except OSError:
            logger.error('problem getting metadata for: {}-{}{}.{}'.format(
                rs.user.username, rs.syllable.sound, rs.syllable.tone, rs.file_extension
                )
            )
            extension, sample_rate, audio_length = (rs.file_extension, None, None)

        if extension == 'wav' and sample_rate == 44100:
            rs.content_as_wav = rs.content
        else:
            with NamedTemporaryFile(prefix='{}{}_'.format(rs.syllable.sound, rs.syllable.tone),
                    suffix='.{}'.format(extension), delete=remove_files) as ntf:
                ntf.write(rs.content)
                ntf.seek(0)
                uuid = uuid1()
                wavfilename = '/tmp/{}.wav'.format(uuid)

                # -ac is audio channel count
                # -ar is audio sample rate
                cmd = [
                    'avconv', '-i', ntf.name,
                    '-ac', '1', '-ar', '44100', wavfilename
                ]
                with open(os.devnull) as nullfile:
                    retcode = subprocess.call(cmd, stdout=nullfile, stderr=nullfile)
                if retcode:
                    print('\nretcode {} for:\n{}'.format(retcode, ' '.join(cmd)))
                    continue
                with open(wavfilename) as wavfile:
                    rs.content_as_wav = wavfile.read()
                if remove_files:
                    os.unlink(wavfilename)
        rs.normalize_version = NORMALIZE_VERSION
        rs.save()
        print('.', end='')
        sys.stdout.flush()
    print()

def normalize_volume_all(remove_files=True):
    print('Process {} remove intermediary files.'.format('will' if remove_files else 'will not'))
    nrecs = RecordedSyllable.objects.filter(recording_ok=True).count()
    print('Normalizing Volume for {} Samples'.format(nrecs))

    print('. Making normalized version')
    print('o Normalized version already exists')
    print('- Normalized version matches original')
    print('x No wav content to normalize')
    for rs in RecordedSyllable.objects.filter(recording_ok=True).select_related('user', 'syllable'):
        if rs.content_as_normalized_wav and rs.normalize_version == NORMALIZE_VERSION:
            print('o', end='')
            sys.stdout.flush()
            continue

        if not rs.content_as_wav:
            print('x', end='')
            sys.stdout.flush()
            continue
        rs.content_as_normalized_wav = None

        wavfile = NamedTemporaryFile(delete=False)
        hash1 = hashlib.sha224(rs.content_as_wav).hexdigest()
        wavfile.write(rs.content_as_wav)
        wavfile.close()

        p = Popen(['normalize-audio', '-q', wavfile.name])
        if p.wait() != 0:
            print('x', end='')
            sys.stdout.flush()
            continue

        with open(wavfile.name) as f:
            rs.content_as_normalized_wav = f.read()
            rs.normalize_version = NORMALIZE_VERSION
            rs.save()
        os.unlink(wavfile.name)
        hash2 = hashlib.sha224(rs.content_as_normalized_wav).hexdigest()
        if hash1 == hash2:
            print('-', end='')
        else:
            print('.', end='')
            sys.stdout.flush()
    print()

def get_metadata(rs):
    """ Returns the file extension, sample rate, and audio length for the .content
        property of the RecordedSyllable passed.
    """
    logger.info(
        'get_metadata() for rs w/ id ({}), file extension: {}'.format(rs.id, rs.file_extension)
    )
    sys.stdout.flush()
    # In-Memory 'file'
    f = cStringIO.StringIO(rs.content)
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

def strip_silence_all(recalculate=False):
    ''' Copies RecordedSyllable.content_as_normalized_wav to
            RecordedSyllable.content_as_silence_stripped_wav with preceding & trailing silence
            removed.
    '''
    rs_count = RecordedSyllable.objects.filter(recording_ok=True).count()
    print('Stripping silence from {} RecordedSyllable objects'.format(rs_count))
    print('. Stripped silence')
    print('o Silence already stripped, ignoring')
    print('x Error reading RecordedSyllable.content_as_normalized_wav')
    for rs in RecordedSyllable.objects.filter(recording_ok=True):
        if recalculate:
            rs.content_as_silence_stripped_wav = None

        if rs.content_as_silence_stripped_wav and rs.normalize_version == NORMALIZE_VERSION:
            print('o', end='')
            sys.stdout.flush()
            continue

        if rs.content_as_normalized_wav is None:
            print('x', end='')
            sys.stdout.flush()
            continue

        sio_in = cStringIO.StringIO(rs.content_as_normalized_wav)
        stripped_content = strip_silence(sio_in)
        sio_in.close()
        if stripped_content is None:
            print('x', end='')
            sys.stdout.flush()
            continue

        sio_out = cStringIO.StringIO()
        scipy.io.wavfile.write(sio_out, 44100, stripped_content)
        rs.content_as_silence_stripped_wav = sio_out.getvalue()
        sio_out.close()
        rs.normalize_version = NORMALIZE_VERSION
        rs.save()
        print('.', end='')
        sys.stdout.flush()
    print()

def strip_silence(wave_file, show_graph=False):
    ''' Removes low-volume data from the beginning and end of *wave_data*.
    '''
    try:
        sample_rate, wave_data = scipy.io.wavfile.read(wave_file)
    except ValueError as ex:
        if ex.message == "Unknown wave file format":
            return None
    if show_graph:
        from matplotlib import pyplot as plt
        x = numpy.arange(len(wave_data))
        plt.subplot(211)
        plt.plot(x, wave_data)
        plt.subplot(212)

    # make 10ms chunk size
    chunk_size = int(44100.0 * 0.010)
#     print('Chunk size for 10ms: {}'.format(chunk_size))
    signal_start = 0  # Index where silence ends and signal starts
    silence_threshold = 800
    volume_found = 0
    while volume_found < silence_threshold and signal_start < (len(wave_data) - chunk_size):
        chunk = wave_data[signal_start:signal_start + chunk_size]
        volume_found = numpy.mean(abs(chunk))
        signal_start += chunk_size

    volume_found = 0
    signal_end = len(wave_data)
    while volume_found < silence_threshold and signal_end >= chunk_size:
        chunk = wave_data[signal_end - chunk_size:signal_end]
        volume_found = numpy.mean(abs(chunk))
        signal_end -= chunk_size

    stripped_wave_data = wave_data[signal_start:signal_end]
    if show_graph:
        x = numpy.arange(len(stripped_wave_data))
        plt.plot(x, stripped_wave_data)
        plt.show()

    return stripped_wave_data

# Full path to the directory containing this file.
DIRPATH = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    analyze_parser = subparsers.add_parser('analyze', help='Print audio type, bit rate, extension')
    analyze_parser.set_defaults(subcommand='analyze')

    makewav_parser = subparsers.add_parser('makewav', help=\
                                           'Converts the RecordedSyllable .content to 44100Hz '\
                                           'wav format in .content_as_wav')
    makewav_parser.set_defaults(subcommand='makewav')
    makewav_parser.add_argument('--keep-files', dest='keep_files', default=False,
        action='store_true',
        help='Use this flag to keep the before & after audio files from the conversion process'
    )

    normalize_volume_parser = subparsers.add_parser('normalize_volume', help='Normalize the audio volume for all samples')
    normalize_volume_parser.set_defaults(subcommand='normalize_volume')

    stripsilence_parser = subparsers.add_parser('stripsilence', help='Remove preceding/following silence for all samples')
    stripsilence_parser.set_defaults(subcommand='stripsilence')
    stripsilence_parser.add_argument('--recalc', dest='recalc', default=False,
        action='store_true',
        help='If content with silence stripped exists, remove and recalculate'
    )

    stripsilence1_parser = subparsers.add_parser('stripsilence1', help='Remove preceding/following silence for all samples')
    stripsilence1_parser.set_defaults(subcommand='stripsilence1')
    stripsilence1_parser.add_argument('id')

    normalize_parser = subparsers.add_parser('normalize', help='Execute all of the normalization procedures for all samples')
    normalize_parser.set_defaults(subcommand='normalize')

    args = parser.parse_args()

    sys.path.append(DIRPATH)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'script_settings'
    django.setup()

    from hanzi_basics.models import PinyinSyllable
    from tonerecorder.models import RecordedSyllable
    from django.contrib.auth.models import User

    if args.subcommand == 'makewav':
        convert_wav_all(remove_files=not args.keep_files)
    elif args.subcommand == 'normalize_volume':
        normalize_volume_all()
    elif args.subcommand == 'stripsilence':
        strip_silence_all(recalculate=args.recalc)
    elif args.subcommand == 'stripsilence1':
        rs = RecordedSyllable.objects.get(id=args.id)
        print('len(content_as_normalized_wav): {}'.format(len(rs.content_as_normalized_wav)))
        sio_in = cStringIO.StringIO(rs.content_as_normalized_wav)
        stripped_content = strip_silence(sio_in, show_graph=True)
        sio_in.close()
        print('len(stripped_content): {}'.format(len(stripped_content)))
        sio_out = cStringIO.StringIO()
        scipy.io.wavfile.write(sio_out, 44100, stripped_content)
        out_wav_content = sio_out.getvalue()
        sio_out.close()

        with open('stripped.wav', 'w+') as of:
            of.write(out_wav_content)
        print('Wrote "stripped.wav"')
    elif args.subcommand == 'normalize':
        normalize_all()
    else:
        raise Exception('Unexpected subcommand {}'.format(args.subcommand))
