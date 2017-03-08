'''
Created on Apr 21, 2016

@author: jivan
'''
from __future__ import print_function

import argparse
import hashlib
import logging
import os, sys
import re
import shutil

import django
from django.db import transaction
from django.db.transaction import atomic
from django.db.utils import IntegrityError

from tonerecorder.models import RecordedSyllable


logger = logging.getLogger(__name__)

def file_metadata(filepath):
    ''' Returns a dictionary with information on the contents of the file (based on the filename).
        Keys are: 'speaker_name', 'sound', 'tone', 'pipeline_index', 'pipeline_status_text', 'extension'.
    '''
    filename = os.path.split(filepath)[-1]
    metadata_regex = '(?P<speaker_name>[\w\.]+)--(?P<sound>\w+)--(?P<tone>\d)--'\
                     '(?P<pipeline_index>\d).(?P<pipeline_status_text>\w+).(?P<extension>.*)$'
    result_fields = ['speaker_name', 'sound', 'tone', 'pipeline_index', 'pipeline_status_text', 'extension']
    lower_fields = ['sound', 'pipeline_status_text', 'extension']

    result = re.match(metadata_regex, filename)


    if result:
        metadata = {
            field: result.group(field)
                for field in result_fields
        }
        for field, value in metadata.items():
            if field in lower_fields:
                metadata[field] = value.lower()
    else:
        logger.error('filename "{}" from path "{}" did not match regex'.format(filename, filepath))
        metadata = None

    return metadata

# text tag for pipeline stage: (position in audio file pipeline,, RecordedSyllable field name for this stage)
pipeline_index_field_by_tag = {
    'original': (0, 'audio_original'),
    'wav': (1, 'audio_wav'),
    'volume_normalized': (2, 'audio_normalized_volume'),
    'silence_stripped': (3, 'audio_silence_stripped'),
}


def load_file(filepath, existing_hashes={}):
    ''' Loads details about *filepath* into the database, not file content.  See file_metadata() for details of
            expected filepath format.
        Returns a RecordedSyllable which needs to be saved on success and
            a string describing the problem on failure from:
            {'original already loaded', 'could not load metadata', 'not a real syllable, skipping', 'db file mismatch'}
            Any other string will be treated as the description of an unexpected error.
    '''
    from django.contrib.auth.models import User
    from hanzi_basics.models import PinyinSyllable
    from tonerecorder.models import RecordedSyllable

    md = file_metadata(filepath)
    if not md:
        return 'could not load metadata'

    user, _ = User.objects.get_or_create(username=md['speaker_name'])
    try:
        syllable = PinyinSyllable.objects.get(sound=md['sound'], tone=md['tone'])
    except PinyinSyllable.DoesNotExist:
        logger.error('No PinyinSyllable "{}{}"'.format(md['sound'], md['tone']))
        return 'not a real syllable, skipping'


    rs, _ = RecordedSyllable.objects.get_or_create(user=user, syllable=syllable)

    # There's special processing for original audio due to a hash for the original audio
    #    to avoid destroying an existing record.
    if md['pipeline_status_text'] == 'original':
        with open(filepath, 'rb') as f:
            content = f.read()

        content_hash = hashlib.md5()
        content_hash.update(content)

        hd = content_hash.hexdigest()
        if hd in existing_hashes.keys():
            ret = 'Duplicate hash "{}" for files {} / {}'.format(hd, existing_hashes[hd], filepath)
        else:
            existing_hashes[hd] = filepath
            if rs.original_md5hex is not None:
                if rs.original_md5hex == content_hash.hexdigest():
                    ret = 'original already loaded'
                else:
                    # If it looks like a mismatch, log a warning and do nothing.
                    msg = "The md5 of the archive file doesn't match the md5 field of an existing db record: {}\n"\
                          "{} != {}.".format(filepath, content_hash.hexdigest(), rs.original_md5hex)
                    logger.warn(msg)

                    ret = 'db file mismatch'
            else:
                rs.audio_original = filepath
                rs.original_md5hex = content_hash.hexdigest()
            rs.save()
            ret = None
    else:
        if md['pipeline_status_text'] == 'wav':
            rs.audio_wav = filepath
        elif md['pipeline_status_text'] == 'volume_normalized':
            rs.audio_normalized_volume = filepath
        elif md['pipeline_status_text'] == 'silence_stripped':
            rs.audio_silence_stripped = filepath
        else:
            msg = 'Unexpected pipeline_status_text: {} for "{}"'.format(md['pipeline_status_text'], filepath)
            logger.error(msg)

        rs.save()
        ret = None

    return ret


def load_all(sample_archive_directory):
    if not os.path.exists(sample_archive_directory):
        raise Exception('Sample Directory "{}" doen\'t exist'.format(sample_archive_directory))

    print('Loading all samples from {} into database.'.format(sample_archive_directory))
    print('. Sample loaded successfully')
    print('- Sample is original audio and already exists in database')
    print('F Error extracting metadata from filename')
    print('m Sample exists in database but doesn\'t match file (See .db-version. files)')
    print('s Sample is for a non-existent pinyin syllable, skipping')
    print('x Unexpected error, see log')
    file_count = 0
    success_count = 0
    # Enable this for speed, disable this to debug specific RecordedSyllable.save() failures
    with atomic():
        for root, dirs, filenames in os.walk(sample_archive_directory):
            # RecordedSyllable instance that have been updated & need to be saved.
            for filename in filenames:
                if 'db-version' in filename:
                    raise Exception('Mismatch dubugging file found in archive: {}'.format(filename))
                filepath = os.path.join(root, filename)
                error = load_file(filepath)

                if error is None:
                    print('.', end='')
                    success_count += 1
                elif error == 'original already loaded':
                    print('-', end='')
                elif error == 'could not load metadata':
                    print('F', end='')
                elif error == 'not a real syllable, skipping':
                    print('s', end='')
                elif error == 'db file mismatch':
                    print('m', end='')
                else:
                    logger.error(error)
                    print('x', end='')
                sys.stdout.flush()

                file_count += 1
        print()
        print('Successfully loaded {}/{} files'.format(success_count, file_count))


def content_filenames(rs):
    """ Creates filenames of a standard format encoding metadata for their content.
        Returns a dict mapping pipeline text to filenames for the file content of the RecordedSyllable passed.
        Ex: {'original': 'somespeaker--du--1--0.original.mp3',
             'wav': 'somespeaker--du--1--1.wav.wav',
             ... }
             
        The string has the form: '<speaker-name>--<sound>--<tone>--<pipeline-index>.<pipeline-text>.<extension>'
    """
#     if rs.recording_ok is None:
#         review_status = 'N'
#     elif rs.recording_ok == True:
#         review_status = 'T'
#     elif rs.recording_ok == False:
#         review_status = 'F'
#     else:
#         raise Exception('Unexpected value for rs.recording_ok: {}'.format(rs.recording_ok))

    filenames_by_pipeline_tag = {}
    for pipeline_tag, (pipeline_index, field_name) in pipeline_index_field_by_tag.items():
        filepath = getattr(rs, field_name)
        if filepath is None:
            output_filename = None
        else:
            ext = os.path.basename(filepath).split('.')[-1]
            output_filename = '{}--{}--{}--{}.{}.{}'.format(
                rs.user.username, rs.syllable.sound.lower(), rs.syllable.tone, pipeline_index, pipeline_tag.lower(), ext.lower()
            )
        filenames_by_pipeline_tag[pipeline_tag] = output_filename


    return filenames_by_pipeline_tag

def content_as_wav_filename(rs):
    """ Returns a filename for the content_as_wav field of the RecordedSyllable passed.
        The string has the form: '<speaker-name>--<sound>--<tone>.wav'
    """
    fname = '{}--{}--{}.wav'.format(rs.user.username, rs.syllable.sound, rs.syllable.tone)
    return fname

def dump_all(archive_dirpath):
    """ Dumps all RecordedSyllables to files in *dirpath*.
        Naming convention is '<speaker-name>--<sound>--<tone>--<review-status>.<review-status-text>.<extension>'
    """
    from tonerecorder.models import RecordedSyllable
    if not os.path.exists(archive_dirpath):
        os.makedirs(archive_dirpath)

    nrecs = RecordedSyllable.objects.count()
    print('Dumping {} Samples to directory "{}"'.format(nrecs, archive_dirpath))
    print('o Adding original file to archive')
    print('w Adding wav file to archive')
    print('n Adding volume_normalized file to archive')
    print('s Adding silence_stripped file to archive')
    print('O DB missing original file')
    print('W DB missing wav file')
    print('N DB missing volume_normalized file')
    print('S DB missing silence_stripped file')
    print('-')
    print('X Unexpected error, see log')

    missing_content = []
    nnone = 0
    ncopied = 0
    for rs in RecordedSyllable.objects.all().select_related('user', 'syllable'):
#         try:
#             os.makedirs(os.path.join(archive_dirpath, rs.user.username))
#         except OSError as exception:
#             if exception.errno != errno.EEXIST:
#                 raise
        fnames_by_tag = content_filenames(rs)

        for pipeline_tag, archive_filename in fnames_by_tag.items():
            (_, field_name) = pipeline_index_field_by_tag[pipeline_tag]
            field_value = getattr(rs, field_name)
            if field_value is None:
                nnone += 1
                if pipeline_tag == 'original':
                    print('O', end='')
                elif pipeline_tag == 'wav':
                    print('W', end='')
                elif pipeline_tag == 'volume_normalized':
                    print('N', end='')
                elif pipeline_tag == 'silence_stripped':
                    print('S', end='')
                else:
                    print('\nUnexpected pipeline tag: {}'.format(pipeline_tag))
            else:
                if not os.path.exists(field_value):
                    missing_content.append('({}): {} / {}'.format(rs.id, pipeline_tag, field_value))
                    continue

                try:
                    archive_filepath = os.path.join(archive_dirpath, archive_filename)
                    if pipeline_tag == 'original':
                        shutil.copyfile(field_value, archive_filepath)
                        print('o', end='')
                    elif pipeline_tag == 'wav':
                        shutil.copyfile(field_value, archive_filepath)
                        print('w', end='')
                    elif pipeline_tag == 'volume_normalized':
                        shutil.copyfile(field_value, archive_filepath)
                        print('n', end='')
                    elif pipeline_tag == 'silence_stripped':
                        shutil.copyfile(field_value, archive_filepath)
                        print('s', end='')
                    ncopied += 1
                except Exception as ex:
                    logger.error(ex)
                    print('X', end='')

    print('\nNo data: {}, Copied to archive: {}'.format(nnone, ncopied))
    if missing_content:
        print('Missing files by RecordedSyllable id:\n{}'.format('\n'.join(missing_content)))

def dump_wav(rs):
    """ Dumps a .wav file from the content_as_wav field of the RecordedSyllable passed.
        Returns the name of the file.
        See content_as_wav_filename() for file naming convention.
    """
    fname = content_as_wav_filename(rs)
    with open(fname, 'wb') as wavfile:
        wavfile.write(rs.content_as_wav)
    return fname

def dump_fully_normalized_wav(rs):
    fname = 'normalized-' + content_as_wav_filename(rs)
    with open(fname, 'wb') as wavfile:
        wavfile.write(rs.content_as_silence_stripped_wav)
    return fname


def remove_nonexistent_paths():
    """ Iterates over all RecordedSyllable instances & sets any audio path field that contains an invalid path to None.
    """
    updated_rss = set()

    for rs in RecordedSyllable.objects.all():
        for _, audio_field in pipeline_index_field_by_tag.values():
            if not os.path.exists(getattr(rs, audio_field)):
                setattr(rs, audio_field, None)
                updated_rss.update({rs})

    logger.info('{} RecordedSyllable instances have non-existent paths'.format(len(updated_rss)))

    with transaction.atomic():
        for rs in updated_rss:
            rs.save()


def remove_empty_recordedsyllables():
    RecordedSyllable.objects.filter(
        audio_original=None, audio_wav=None, audio_normalized_volume=None, audio_silence_stripped=None
    ).delete()


# Full path to the directory containing this file.

DIRPATH = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    load_parser = subparsers.add_parser('load', help='Load files from directory into DB')
    dump_parser = subparsers.add_parser('dump', help='Dump all RecordedSyllables to files')
    helpmsg = 'Dump the .content_as_wav field of a RecordedSyllable to a file'
    dumpwav_parser = subparsers.add_parser('dumpwav', help=helpmsg)

    load_parser.set_defaults(subcommand='load')
    load_parser.add_argument(
        '-d', '--directory', type=str, help='Directory to load audio files from'
    )
    load_parser.set_defaults(directory=os.path.join(DIRPATH, 'sample_archive'))
    dump_parser.set_defaults(subcommand='dump')
    dump_parser.add_argument(
        '-d', '--directory', type=str, help='Directory to dump audio files to'
    )
    dump_parser.set_defaults(directory=os.path.join(DIRPATH, 'sample_archive'))
    dumpwav_parser.set_defaults(subcommand='dumpwav')
    dumpwav_parser.add_argument(
        'rsid', type=int, help='Id of the RecordedSyllable to dump as .wav'
    )
    dumpnormal_parser = subparsers.add_parser('dumpnormal', help=helpmsg)
    dumpnormal_parser.set_defaults(subcommand='dumpnormal')
    dumpnormal_parser.add_argument(
        'rsid', type=int, help='Id of the RecordedSyllable to dump as .wav'
    )

    args = parser.parse_args()

    sys.path.append(DIRPATH)
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'script_settings'
    django.setup()

    from hanzi_basics.models import PinyinSyllable
    from tonerecorder.models import RecordedSyllable
    from django.contrib.auth.models import User


    if args.subcommand == 'load':
        load_all(args.directory)
    elif args.subcommand == 'dump':
        dump_all(args.directory)
    elif args.subcommand == 'dumpwav':
        rs = RecordedSyllable.objects.get(id=args.rsid)
        dump_wav(rs)
    elif args.subcommand == 'dumpnormal':
        rs = RecordedSyllable.objects.get(id=args.rsid)
        dump_fully_normalized_wav(rs)
    else:
        raise Exception('Unexpected subcommand {}'.format(args.subcommand))
