'''
Created on April 8, 2016

@author: jivan
'''
import os
SECRET_KEY = 'Not important for testing'
DEBUG = False

DIRPATH = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))
DBPATH = os.path.join(DIRPATH, 'samples.sqlite3')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DBPATH
    }
}

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'webvdc',
#        'USER': 'webvdc',
#        'PASSWORD': 'webvdc',
#    }
#}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'hanzi_basics',
    'tonerecorder',
)
