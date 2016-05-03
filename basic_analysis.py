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

import django
from django.core.files.temp import NamedTemporaryFile
import mutagen.mp3
import taglib


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
    nrecs = RecordedSyllable.objects.count()
    print('Converting {} Samples'.format(nrecs))

    for rs in RecordedSyllable.objects.all().select_related('user', 'syllable'):
        if rs.content_as_wav:
            print('o', end='')
            sys.stdout.flush()
            continue

        try:
            extension, sample_rate, audio_length = get_metadata(rs)
        except OSError:
            print('problem getting metadata for: {}-{}{}.{}'.format(
                rs.user.username, rs.syllable.sound, rs.syllable.tone, rs.file_extension
                )
            )
            continue

        if extension == 'wav' and sample_rate == 44100:
            rs.content_as_wav = rs.content
        else:
            with NamedTemporaryFile(prefix='{}{}_'.format(rs.syllable.sound, rs.syllable.tone),
                    suffix='.{}'.format(extension), delete=remove_files) as ntf:
                ntf.write(rs.content)
                uuid = uuid1()
                wavfilename = '/tmp/{}.wav'.format(uuid)

                # -ac is audio channel count
                # -ar is audio sample rate
                cmd = [
                    'avconv', '-i', ntf.name,
                    '-ac', '1', '-ar', '44100', wavfilename
                ]
                with open(os.devnull) as nullfile:
                    error = subprocess.call(cmd, stdout=nullfile, stderr=nullfile)
                if error:
                    print('\nproblem with: {}'.format(ntf.name))
                    sys.stdout.flush()
                    continue
                with open(wavfilename) as wavfile:
                    rs.content_as_wav = wavfile.read()
                if remove_files:
                    os.unlink(wavfilename)
        rs.save()
        print('.', end='')
        sys.stdout.flush()

def normalize_volume_all(remove_files=True):
    print('Process {} remove intermediary files.'.format('will' if remove_files else 'will not'))
    nrecs = RecordedSyllable.objects.count()
    print('Normalizing Volume for {} Samples'.format(nrecs))

    for rs in RecordedSyllable.objects.all().select_related('user', 'syllable'):
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
            rs.save()
        os.unlink(wavfile.name)
        hash2 = hashlib.sha224(rs.content_as_normalized_wav).hexdigest()
        if hash1 == hash2:
            print('-', end='')
        else:
            print('.', end='')
            sys.stdout.flush()
    print()

def analyze_all():
    nrecs = RecordedSyllable.objects.count()
    print('Analyzing {} Samples'.format(nrecs))

    for rs in RecordedSyllable.objects.all().select_related('user', 'syllable'):
        extension, sample_rate, audio_length = get_metadata(rs)
        print(extension, sample_rate, audio_length)

def get_metadata(rs):
    """ Returns the file extension, sample rate, and audio length for the .content
        property of the RecordedSyllable passed.
    """
    # In-Memory 'file'
    f = cStringIO.StringIO(rs.content)
    audio_details = sndhdr.whathdr_stringio(f)

    if audio_details:
        (type, sample_rate, channels, frames, bits_per_sample) = audio_details
        audio_metadata = (rs.file_extension, sample_rate, None)
    else:
        ntf = NamedTemporaryFile(delete=False, suffix='.{}'.format(rs.file_extension))
        ntf.write(rs.content)
        ntf.close()

        try:
            tlinfo = taglib.File(ntf.name)
            sample_rate = tlinfo.sampleRate
            audio = mutagen.mp3.MP3(ntf.name)
            audio_length = audio.info.length
            audio_metadata = (rs.file_extension, sample_rate, audio_length)
        finally:
            os.unlink(ntf.name)

    return audio_metadata

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

    normalize_parser = subparsers.add_parser('normalize', help='Normalize the audio volume for all samples')
    normalize_parser.set_defaults(subcommand='normalize')

    args = parser.parse_args()

    sys.path.append(DIRPATH)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'script_settings'
    django.setup()

    from hanzi_basics.models import PinyinSyllable
    from tonerecorder.models import RecordedSyllable
    from django.contrib.auth.models import User

    if args.subcommand == 'analyze':
        analyze_all()
    if args.subcommand == 'makewav':
        convert_wav_all(remove_files=not args.keep_files)
    if args.subcommand == 'normalize':
        normalize_volume_all()
    else:
        raise Exception('Unexpected subcommand {}'.format(args.subcommand))
