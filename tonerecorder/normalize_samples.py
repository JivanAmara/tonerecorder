'''
Created on Apr 21, 2016

@author: jivan
'''
from __future__ import print_function

from Tkinter import Tk
import argparse
import cStringIO
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

import django
from guppy import hpy
import mutagen.mp3
import taglib
from tkSnack import initializeSnack, Sound

import resource  # @UnresolvedImport


logger = logging.getLogger(__name__)

root = Tk()
initializeSnack(root)

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

def convert_wav(infile_path, outfile_path):
    ''' *brief*: Converts *infile_path* to a single channel wav file with sampling rate of 44100
            and writes the result to *outfile_path*.
    '''
    extension, sample_rate, audio_length = get_file_metadata(infile_path)
    if extension is None:
        raise Exception('infile_path has invalid audio extension')

    if extension == 'wav' and sample_rate == 44100:
        shutil.copy(infile_path, outfile_path)
    else:
        # -ac is audio channel count
        # -ar is audio sample rate
        cmd = [
            'avconv', '-i', infile_path,
            '-ac', '1', '-ar', '44100', outfile_path
        ]
        with open(os.devnull) as nullfile:
#             retcode = subprocess.call(cmd, stdout=nullfile, stderr=nullfile)
            p = Popen(cmd, stdout=nullfile, stderr=nullfile)
        p.wait()
        if p.returncode != 0:
            msg = '\nretcode {} for:\n{}'.format(p.returncode, ' '.join(cmd))
            logger.error(msg)
            raise Exception(msg)

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

def normalize_volume(infile_path, outfile_path):
    ''' *brief*: Uses command-line tool 'normalize-audio' to normalize the volume of *infile_path*
            and writing the normalized audio to *outfile_path*
    '''
    try:
        shutil.copyfile(infile_path, outfile_path)
        cmd = ['normalize-audio', '-q', outfile_path]
        p = Popen(cmd)
        p.wait()
        if p.returncode != 0:
            msg = 'Non-zero return code {} from {}'.format(p.returncode, cmd)
            logger.error(msg)
            raise Exception(msg)
    except:
        os.unlink(outfile_path)
        raise

def normalize_volume_all(remove_files=True):
    print('Process {} remove intermediary files.'.format('will' if remove_files else 'will not'))
    nrecs = RecordedSyllable.objects.filter(recording_ok=True).count()
    print('Normalizing Volume for {} Samples'.format(nrecs))

    print('. Making normalized version')
    print('o Normalized version already exists')
    print('- Normalized version matches original')
    print('x No wav content to normalize')
    # Break the RecordedSyllable retrieval up into chunks to limit memory usage.
    qschunksize = 500
    qschunks = [
        RecordedSyllable.objects.filter(recording_ok=True)\
            .select_related('user', 'syllable')[i:i + qschunksize]
            for i in range(0, nrecs - qschunksize, qschunksize)
    ]
    for qschunk in qschunks:
        for rs in qschunk:
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

def strip_silence(infile_path, outfile_path):
    try:
        s = Sound()
        s.load(infile_path)

        pitches = s.pitch()
        if pitches is None:
            return None

        sample_count = s.length()

        # Determine the segments of continuous non-zero pitch as 2-tuples (start-idx, end-idx)
        nonzero_segments = []
        start = None
        end = None
        for i, p in enumerate(pitches):
            if start is None and p == 0.0:
                continue
            elif start is None and p != 0.0:
                start = i
            elif start is not None and p == 0.0:
                end = i - 1
                nonzero_segments.append((start, end))
                start = None
                end = None
                continue
            elif start is not None and i == (len(pitches) - 1):
                end = i
                nonzero_segments.append((start, end))

        # Determine the longest segment and cut the sound to only include those samples
        longest_segment = (0, 0)
        for nzs in nonzero_segments:
            if nzs[1] - nzs[0] > longest_segment[1] - longest_segment[0]:
                longest_segment = nzs
        samples_per_pitch_value = sample_count / float(len(pitches))
        longest_segment_in_samples = (
            int(samples_per_pitch_value * longest_segment[0]),
            int(samples_per_pitch_value * longest_segment[1])
        )

        # If there's nothing left, raise an exception
        if longest_segment_in_samples[1] - longest_segment_in_samples[0] == 0:
            raise('No data left after stripping')
        # We're good to go, write the trimmed audio.
        else:
            s.cut(longest_segment_in_samples[1], sample_count - 1)
            s.cut(0, longest_segment_in_samples[0])

            s.write(outfile_path)
    finally:
        # tkSnack is a c library and the memory it uses won't get garbage collected.
        # Release the memory it's using with this.
        s.destroy()

def strip_silence_all(recalculate=False):
    ''' Copies RecordedSyllable.content_as_normalized_wav to
            RecordedSyllable.content_as_silence_stripped_wav with preceding & trailing silence
            removed.
    '''
    rs_count = RecordedSyllable.objects.filter(recording_ok=True)\
                   .exclude(content_as_normalized_wav=None).count()
    print('Stripping silence from {} RecordedSyllable objects'.format(rs_count))
    print('. Stripped silence')
    print('o Silence already stripped, ignoring')
    print('x Error reading RecordedSyllable.content_as_normalized_wav')
    rschunksize = 1000
    for chunkstart in range(0, rs_count - rschunksize, rschunksize):
        print('Memory usage before chunk[{}:{}]: {}'\
              .format(
                  chunkstart, chunkstart + rschunksize,
                  resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        )
        rschunk = RecordedSyllable.objects.filter(recording_ok=True)\
            .exclude(content_as_normalized_wav=None)\
            .select_related('user', 'syllable')[chunkstart:chunkstart + rschunksize].iterator()


#         hp = hpy()
#         before = hp.heap()
#         leftovers = []
        for rs in rschunk:
            if recalculate:
                rs.content_as_silence_stripped_wav = None

            if rs.content_as_silence_stripped_wav is not None \
                and rs.normalize_version == NORMALIZE_VERSION:
                print('o', end='')
                sys.stdout.flush()
                continue

            if rs.content_as_normalized_wav is None:
                print('x', end='')
                sys.stdout.flush()
                continue

            stripped_content = strip_silence_from_data(rs.content_as_normalized_wav)

            if stripped_content is None:
                print('x', end='')
                sys.stdout.flush()
                continue

            rs.content_as_silence_stripped_wav = stripped_content
            rs.normalize_version = NORMALIZE_VERSION
#             leftovers.append(hp.heap() - before)
            rs.save()
#             leftovers.append(hp.heap() - before)
            print('.', end='')
            sys.stdout.flush()
        print('Memory usage after chunk[{}:{}]: {}'\
              .format(
                  chunkstart, chunkstart + rschunksize,
                  resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        )
#         for i, leftover in enumerate(leftovers):
#             print('Heap diff{}:\n{}'.format(i, leftover))

def strip_silence_from_data(wave_file_data):
    # Write wave data to a file so ntSnack can load it.
    with NamedTemporaryFile() as ntf:
        ntf.write(wave_file_data)
        s = Sound()
        s.load(ntf.name)

    pitches = s.pitch()
    if pitches is None:
        return None

    sample_count = s.length()

    # Determine the segments of continuous non-zero pitch as 2-tuples (start-idx, end-idx)
    nonzero_segments = []
    start = None
    end = None
    for i, p in enumerate(pitches):
        if start is None and p == 0.0:
            continue
        elif start is None and p != 0.0:
            start = i
        elif start is not None and p == 0.0:
            end = i - 1
            nonzero_segments.append((start, end))
            start = None
            end = None
            continue
        elif start is not None and i == (len(pitches) - 1):
            end = i
            nonzero_segments.append((start, end))

    # Determine the longest segment and cut the sound to only include those samples
    longest_segment = (0, 0)
    for nzs in nonzero_segments:
        if nzs[1] - nzs[0] > longest_segment[1] - longest_segment[0]:
            longest_segment = nzs
    samples_per_pitch_value = sample_count / float(len(pitches))
    longest_segment_in_samples = (
        int(samples_per_pitch_value * longest_segment[0]),
        int(samples_per_pitch_value * longest_segment[1])
    )

    # If there's nothing left, return None
    if longest_segment_in_samples[1] - longest_segment_in_samples[0] == 0:
        stripped_content = None
    else:
        s.cut(longest_segment_in_samples[1], sample_count - 1)
        s.cut(0, longest_segment_in_samples[0])

        with NamedTemporaryFile(suffix='.wav') as ntfout:
            s.write(ntfout.name)
            ntfout.seek(0)
            stripped_content = ntfout.read()
        s.destroy()

    return stripped_content


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
        stripped_content = strip_silence_from_data(rs.content_as_normalized_wav)
        print('len(stripped_content): {}'.format(len(stripped_content)))

        out_wav_content = stripped_content

        with open('stripped.wav', 'w+') as of:
            of.write(out_wav_content)
        print('Wrote "stripped.wav"')
    elif args.subcommand == 'normalize':
        normalize_all()
    else:
        raise Exception('Unexpected subcommand {}'.format(args.subcommand))
