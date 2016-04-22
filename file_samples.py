'''
Created on Apr 21, 2016

@author: jivan
'''
from __future__ import print_function
import argparse
import os, sys
import re
import django
from _ast import Raise

def file_metadata(filepath):
    ''' Returns a dictionary with information on the contents of the file (based on the filename).
        Keys are: 'speaker_name', 'sound', 'tone', 'extension'.
    '''
    filename = os.path.split(filepath)[1]
    metadata_regex = '(?P<speaker_name>\w+)--\d--(?P<sound>\w+)--(?P<tone>\d)--\d.(?P<extension>.*)$'
    result = re.match(metadata_regex, filename)

    if result:
        metadata = {
            field: result.group(field) for field in ['speaker_name', 'sound', 'tone', 'extension']
        }
    else:
        metadata = None

    return metadata

def load_file(filename):
    md = file_metadata(filename)
    if not md:
        return 'could not load metadata'
    
    user, created = User.objects.get_or_create(username=md['speaker_name'])
    try:
        syllable = PinyinSyllable.objects.get(sound=md['sound'], tone=md['tone'])
    except PinyinSyllable.DoesNotExist:
        return 'not a real syllable, skipping'

    with open(filename) as f:
        content = f.read()
    rs = RecordedSyllable(
        user=user, syllable=syllable, content=content, file_extension=md['extension']
    )
    try:
        rs.save()
    except django.db.IntegrityError:
        return 'already loaded'

def dump_all(dirpath):
    """ Dumps all RecordedSyllables to files in *dirpath*.
        Naming convention is '<speaker-name>--0--<sound>--<tone>--0.<extension>'
    """
    os.makedirs(dirpath)
    nrecs = RecordedSyllable.objects.count()
    print('Dumping {} Samples'.format(nrecs))

    for rs in RecordedSyllable.objects.all().select_related('user', 'syllable'):
        fname = '{}--0--{}--{}--0.{}'.format(
            rs.user.username, rs.syllable.sound, rs.syllable.tone, rs.file_extension
        )
        with open(os.path.join(dirpath, fname), 'w+') as f:
            f.write(rs.content)
        print('.', end='')
    

# Full path to the directory containing this file.
DIRPATH = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    load_parser = subparsers.add_parser('load', help='Load files from directory into DB')
    dump_parser = subparsers.add_parser('dump', help='Dump all RecordedSyllables to files')
    load_parser.set_defaults(subcommand='load')
    load_parser.add_argument(
        'directory', type=str, help='Directory to load audio files from'
    )
    dump_parser.set_defaults(subcommand='dump')
    dump_parser.add_argument(
        'directory', type=str, help='Directory to dump audio files to'
    )

    args = parser.parse_args()

    sys.path.append(DIRPATH)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'script_settings'
    django.setup()
 
    from hanzi_basics.models import PinyinSyllable
    from tonerecorder.models import RecordedSyllable
    from django.contrib.auth.models import User
 
    
    if args.subcommand == 'load':
        print('Collecting files from {}'.format(args.directory))
        for dirpath, dirnames, filenames in os.walk(args.directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                print('loading {}...'.format(filepath), end='')
                error = load_file(filepath)
                if error:
                    print(error)
                else:
                    print('done.')
    elif args.subcommand == 'dump':
        dump_all(args.directory)
    else:
        raise Exception('Unexpected subcommand {}'.format(args.subcommand))
