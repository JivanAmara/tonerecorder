'''
Created on May 20, 2016

@author: jivan
'''
import sys, os
import django

if __name__ == '__main__':
    # The path to the directory containing 'tonerecorder' python package.
    DIRPATH = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir))
    sys.path.append(DIRPATH)

    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tonerecorder.script_settings'
    django.setup()
    from tonerecorder.models import RecordedSyllable

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
