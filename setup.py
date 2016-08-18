from setuptools import setup
import os

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# README file
with open('README.rst', 'r') as rmf:
    README = rmf.read()

setup(
    name="tonerecorder",
    version="1.1.0.dev0",
    author="Jivan Amara",
    author_email="Development@JivanAmara.net",
    packages=['tonerecorder', 'tonerecorder.migrations',
              'tonerecorder.management', 'tonerecorder.management.commands'],
    package_data={
        'tonerecorder': [
            'requirements.txt',
            'templates/record-html5-mobile.html'
        ],
    },
    description='Django app for recording Pinyin syllables',
    long_description=README,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
    ],
)
