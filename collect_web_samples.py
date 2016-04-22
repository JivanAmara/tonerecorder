'''
Created on Apr 8, 2016

@author: jivan
'''
from __future__ import print_function, unicode_literals
import os
import sys
from time import sleep
import django
from django.conf import settings
from django.test.utils import get_runner
import urllib3
# Until python 2.7.9 is packaged for Ubuntu, use this to eliminate SNIMissingWarning
#    See: https://urllib3.readthedocs.org/en/latest/security.html#snimissingwarning
urllib3.disable_warnings()
from django.db.utils import IntegrityError

# Full path to the directory containing this file.
DIRPATH = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))

sample_sources = [
    {
        'speaker_name': 'chinesepod.com',
        'url_pattern': 'http://chinesepod.com/mp3/pinyin/<sound><tone>.mp3',
        'file_extension': 'mp3',
    },
    {
        'speaker_name': 'yoyochinese.com',
        'url_pattern': 'https://www.yoyochinese.com/files/<sound><tone>.mp3',
        'file_extension': 'mp3',
    },
    {
        'speaker_name': 'standardmandarin.com',
        'url_pattern': 'http://www.standardmandarin.com/Sound_Resources/Syllables/<sound><tone>.mp3',
        'file_extension': 'mp3',
    },
]

def collect_sample(speaker_name, url_pattern, file_extension, pinyin):
    ''' Download the audio file for *pinyin* (in sound-tone representation) using
            *url_pattern* which should have '<sound>' and '<tone>' tokens in it.
            *speaker_name* is the name to use when saving the sample.
    '''
    if not ('<sound>' in pinyin and '<tone>' in pinyin):
        msg = 'url_pattern must contain "<sound>" and "<tone>":\n  {}'.format(url_pattern)

    pinyin_syllable = PinyinSyllable.objects.get(sound=pinyin[:-1], tone=pinyin[-1])
    user, ignore_created_flag = User.objects.get_or_create(username=speaker_name)
    try:
        rs = RecordedSyllable.objects.get(
                user__username=speaker_name,
                syllable__sound=pinyin[:-1],
                syllable__tone=pinyin[-1]
        )
        syllable_already_collected = True
    except RecordedSyllable.DoesNotExist:
        syllable_already_collected = False

    if syllable_already_collected:
        status = 'already_collected'
    else:
        url = url_pattern.replace('<sound>', pinyin[:-1]).replace('<tone>', pinyin[-1])
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        if r.status != 200:
            status = 'failed'
        else:
            data = r.data
            rc = RecordedSyllable(
                    user=user, syllable=pinyin_syllable, content=data, file_extension=file_extension
                 )
            rc.save()
            status = 'collected'

    return status

if __name__ == "__main__":
    # Run first with 'migrate', then 'populate_hanzi_basics' to set up the database.
    try:
        command = sys.argv[1]
    except:
        command = None

    sys.path.append(DIRPATH)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'script_settings'
    django.setup()

    if command == 'makefile':
        pinyin = sys.argv[2]
        speaker_name = sys.argv[3]
        from hanzi_basics.models import PinyinSyllable
        from tonerecorder.models import RecordedSyllable
        from django.contrib.auth.models import User
        rs = RecordedSyllable.objects.get(
            syllable__sound=pinyin[:-1], syllable__tone=pinyin[-1], user__username=speaker_name
        )
        with open('{}-{}.{}'.format(pinyin, speaker_name, rs.file_extension), 'w+') as f:
            f.write(rs.content)
    elif command:
        from django.core.management import call_command
        call_command(command)
    else:
        from hanzi_basics.models import PinyinSyllable
        from tonerecorder.models import RecordedSyllable
        from django.contrib.auth.models import User

        print('a: Already Collected, <n>: source collected from')
        print('Sources:')
        for i, source in enumerate(sample_sources):
            print('{}: {}'.format(i, source['speaker_name']))
        print('--------')
        problem_pinyin = []
        for ps in PinyinSyllable.objects.order_by('sound', 'tone'):
            pinyin = '{}{}'.format(ps.sound, ps.tone)
            print('{}: '.format(ps.display), end='')
            sys.stdout.flush()
            fail_count = 0
            for i, source in enumerate(sample_sources):
                status = collect_sample(source['speaker_name'], source['url_pattern'], source['file_extension'], pinyin)
                if status == 'already_collected':
                    print('a', end='')
                elif status == 'failed':
                    print('f', end='')
                    fail_count += 1
                elif status == 'collected':
                    print(i, end='')
                else:
                    print('Unexpected status: {}'.format(status))
                sys.stdout.flush()

            if fail_count == 3:
                problem_pinyin.append('{}{}'.format(ps.sound, ps.tone))
#                 if status in ['failed', 'collected']:
#                     sleep(0.08)
            print()
        print()
        print('Problem Pinyin:\n{}'.format(problem_pinyin))
