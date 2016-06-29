'''
Created on Apr 21, 2016

@author: jivan
'''
from __future__ import print_function

import argparse
import errno
import hashlib
import os, sys
import re

import django


def file_metadata(filepath):
    ''' Returns a dictionary with information on the contents of the file (based on the filename).
        Keys are: 'speaker_name', 'sound', 'tone', 'review_status', 'extension'.
    '''
    filename = os.path.split(filepath)[1]
    metadata_regex = '(?P<speaker_name>[\w\.]+)--(?P<sound>\w+)--(?P<tone>\d)--(?P<review_status>\w).(?P<extension>.*)$'
    result = re.match(metadata_regex, filename)

    if result:
        metadata = {
            field: result.group(field)
                for field in ['speaker_name', 'sound', 'tone', 'review_status', 'extension']
        }
    else:
        metadata = None

    return metadata

def load_file(filepath):
    ''' Loads the contents of *filepath* into the database.  See file_metadata() for details of
            expected filepath format.
        Returns None on success and a string describing the problem on failure.
    '''
    from django.contrib.auth.models import User
    from hanzi_basics.models import PinyinSyllable
    from tonerecorder.models import RecordedSyllable

    md = file_metadata(filepath)
    if not md:
        return 'could not load metadata'

    user, created = User.objects.get_or_create(username=md['speaker_name'])
    try:
        syllable = PinyinSyllable.objects.get(sound=md['sound'], tone=md['tone'])
    except PinyinSyllable.DoesNotExist:
        return 'not a real syllable, skipping'

    try:
        rs = RecordedSyllable.objects.get(
                         user=user, syllable__sound=md['sound'], syllable__tone=md['tone'])
    except RecordedSyllable.DoesNotExist:
        rs = None

    with open(filepath) as f:
        content = f.read()

    # If an existing entry in the database exists, check that it matches the contents of
    #    the file.
    if rs:
        rs_hash = hashlib.md5()
        content_hash = hashlib.md5()
        rs_hash.update(rs.content)
        content_hash.update(content)
        if rs_hash.hexdigest() != content_hash.hexdigest():
            # if the file doesn't match the database content, save the database content
            #    using the filepath with '.db-version' before the extension
            db_filepath = re.sub(r'(.*)\.(.*)', r'\1.db-version.\2', filepath)
            with open(db_filepath, 'wb') as db_file:
                db_file.write(rs.content)
            ret = 'db file mismatch'
        else:
            ret = 'already loaded'
    else:
        if md['review_status'] == 'N':
            review_status = None
        elif md['review_status'] == 'T':
            review_status = True
        elif md['review_status'] == 'F':
            review_status = False
        else:
            raise Exception('Unexpected review_status code: {}'.format(md['review_status']))

        rs = RecordedSyllable(
            user=user, syllable=syllable, content=content,
            recording_ok=review_status, file_extension=md['extension']
        )
        rs.save()
        ret = None

    return ret


def load_all(sample_archive_directory):
    if not os.path.exists(sample_archive_directory):
        raise Exception('Sample Directory "{}" doen\'t exist'.format(sample_archive_directory))

    print('Loading all samples from {} into database.'.format(sample_archive_directory))
    print('. Sample loaded successfully')
    print('- Sample already exists in database')
    print('x Error loading sample')
    print('m Sample exists in database but doesn\'t match file (See .db-version. files)')
    print('s Sample is for a non-existent pinyin syllable, skipping')
    file_count = 0
    for root, dirs, filenames in os.walk(sample_archive_directory):
        for filename in filenames:
            if 'db-version' in filename:
                raise Exception('Mismatch dubugging file found in archive: {}'.format(filename))
            filepath = os.path.join(root, filename)
            error = load_file(filepath)

            if error == 'already loaded':
                print('-', end='')
            elif error is None:
                print('.', end='')
            elif error == 'could not load metadata':
                print('x', end='')
            elif error == 'not a real syllable, skipping':
                print('s', end='')
            elif error == 'db file mismatch':
                print('m', end='')
            else:
                raise Exception('Unexpected return value for load_file(): {}'.format(error))
            sys.stdout.flush()

            file_count += 1
    print()
    print('{} sample files loaded'.format(file_count))

def content_filename(rs):
    """ Returns a filename for the content field of the RecordedSyllable passed.
        The string has the form: '<speaker-name>--<sound>--<tone>--<review-status>.<extension>'
    """
    if rs.recording_ok is None:
        review_status = 'N'
    elif rs.recording_ok == True:
        review_status = 'T'
    elif rs.recording_ok == False:
        review_status = 'F'
    else:
        raise Exception('Unexpected value for rs.recording_ok: {}'.format(rs.recording_ok))

    fname = '{}--{}--{}--{}.{}'.format(
        rs.user.username, rs.syllable.sound, rs.syllable.tone, review_status, rs.file_extension
    )
    return fname

def content_as_wav_filename(rs):
    """ Returns a filename for the content_as_wav field of the RecordedSyllable passed.
        The string has the form: '<speaker-name>--<sound>--<tone>.wav'
    """
    fname = '{}--{}--{}.wav'.format(rs.user.username, rs.syllable.sound, rs.syllable.tone)
    return fname

def dump_all(dirpath):
    """ Dumps all RecordedSyllables to files in *dirpath*.
        Naming convention is '<speaker-name>--<sound>--<tone>--<review-status>.<extension>'
    """
    from tonerecorder.models import RecordedSyllable
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    nrecs = RecordedSyllable.objects.count()
    print('Dumping {} Samples to directory "{}"'.format(nrecs, dirpath))
    print('. Dumping content not in archive')
    print('! Will re-dump content because archive file doesn\'t match content')
    print('o Archive file exists and matches content')
    print('x No content for recorded syllable')
    missing_content = []
    for rs in RecordedSyllable.objects.all().select_related('user', 'syllable'):
        try:
            os.makedirs(os.path.join(dirpath, rs.user.username))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        fname = os.path.join(rs.user.username, content_filename(rs))
        fpath = os.path.join(dirpath, fname)

        if not rs.content:
            print('x', end='')
            sys.stdout.flush()
            rs_desc = '{}: {}{} (id: {})'.format(
                          rs.user.username, rs.syllable.sound, rs.syllable.tone, rs.id
                      )
            missing_content.append(rs_desc)
            continue

        # Check that an existing dump matches the current db content
        if os.path.exists(fpath):
            with open(fpath, 'rb') as f:
                file_hash = hashlib.md5()
                file_hash.update(f.read())
            content_hash = hashlib.md5()
            content_hash.update(rs.content)
            if file_hash.digest() == content_hash.digest():
                dump_content = False
                print('o', end='')
                sys.stdout.flush()
            else:
                print('!', end='')
                dump_content = True
                sys.stdout.flush()
        else:
            dump_content = True

        # If there's no existing dump, or the content doesn't match the dump, dump to file.
        if dump_content:
            with open(fpath, 'wb') as f:
                f.write(rs.content)
            print('.', end='')
            sys.stdout.flush()
    print()
    if missing_content:
        print('Missing .content for files:\n{}'.format('\n'.join(missing_content)))

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
