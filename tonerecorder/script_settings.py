'''
Created on April 8, 2016

@author: jivan
'''
import os
SECRET_KEY = 'Not important for testing'
DEBUG = False

DIRPATH = os.path.abspath(os.path.dirname(__file__))
DBPATH = os.path.join(DIRPATH, 'samples.sqlite3')

MEDIA_ROOT = os.path.join(DIRPATH, 'tonerecorder-media')
SYLLABLE_AUDIO_DIR = 'audio-files'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DBPATH
    }
}

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'webvdc',
#        'USER': 'webvdc',
#        'PASSWORD': 'webvdc',
#    }
# }

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'hanzi_basics',
    'tonerecorder',
)
