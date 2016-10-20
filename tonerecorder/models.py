'''
Created on Mar 16, 2016

@author: jivan
'''
from __future__ import unicode_literals

import datetime
from fileinput import filename
import hashlib
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.utils.encoding import python_2_unicode_compatible
from hanzi_basics.models import PinyinSyllable
import logging
logger = logging.getLogger(__name__)

@python_2_unicode_compatible
class RecordedSyllable(models.Model):
    ''' Except for the original audio, all audio files are .wav format.
        Different versions build on each other in the order presented,
        e.g. audio_silence_stripped points to a file that has been converted to
        .wav, had its volume normalized, and had its silence stripped.
        
        The location of files is determined by settings MEDIA_ROOT and SYLLABLE_AUDIO_DIR.
        The naming uses a standard format derived from this model's values.
        
        Use create_audio_path() to get a valid value for audio_* attributes.
    '''
    native = models.BooleanField(default=False)
    recording_ok = models.NullBooleanField()
    user = models.ForeignKey(User, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    syllable = models.ForeignKey(PinyinSyllable)

    original_md5hex = models.CharField(max_length=32, unique=True, null=True, blank=True)

    # Full path to original audio
    audio_original = models.CharField(max_length=200, null=True)
    # Full path to audio converted to mp3
    audio_mp3 = models.CharField(max_length=200, null=True)
    # Full path to audio converted to wav
    audio_wav = models.CharField(max_length=200, null=True)
    # Full path to audio with normalized volume
    audio_normalized_volume = models.CharField(max_length=200, null=True)
    # Full path to audio with silence stripped
    audio_silence_stripped = models.CharField(max_length=200, null=True)

    file_extension = models.CharField(max_length=40)
    # This text is used to determine if normalization should be redone.
    normalize_version = models.CharField(max_length=10)

    def create_audio_path(self, audio_version):
        ''' *rs* is a RecordedSyllable instance
            *audio_version* should be one of:
                'original', 'mp3', 'wav', 'volume_normalized', 'silence_stripped'.
        '''
        pipeline_states = ['original', 'mp3', 'wav', 'volume_normalized', 'silence_stripped']
        if audio_version not in pipeline_states:
            raise(Exception('{} not a recognized audio sample state'.format(audio_version)))
        pipeline_index = pipeline_states.index(audio_version)

        if audio_version == 'mp3':
            file_extension = 'mp3'
        elif audio_version == 'original':
            file_extension = self.file_extension
        else:
            file_extension = 'wav'

        if not hasattr(self, 'native') or self.native == True:
            filename_template = '{speaker}--{sound}--{tone}--{index}.{audio_version}.{extension}'
            timestamp = None
        else:
            filename_template = \
                '{speaker}--{sound}--{tone}--{timestamp}--{index}.{audio_version}.{extension}'
            timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

        username = 'None' if self.user is None else self.user.username

        filename = filename_template.format(
                        speaker=username,
                        sound=self.syllable.sound,
                        tone=self.syllable.tone,
                        timestamp=timestamp,
                        index=pipeline_index,
                        audio_version=audio_version,
                        extension=file_extension,
                        )

        os.makedirs(os.path.join(settings.MEDIA_ROOT, settings.SYLLABLE_AUDIO_DIR), exist_ok=True)
        audio_path = os.path.join(settings.MEDIA_ROOT, settings.SYLLABLE_AUDIO_DIR, filename)
        return audio_path

    @staticmethod
    def set_md5hex(sender=None, instance=None, **kwargs):
        with open(instance.audio_original, 'rb') as f:
            m = hashlib.md5()
            m.update(f.read())
            md5hex = m.hexdigest()
            if instance.original_md5hex is not None and instance.original_md5hex != md5hex:
                msg = 'MD5 changed for RecordedSyllable.audio_original with id: {}'\
                          .format(instance.id)
                logger.warn(msg)
            instance.original_md5hex = md5hex

    def __str__(self):
        u_syl = "{}".format(self.syllable)

        urep = "{0}: {1}"\
                   .format(self.user.username, u_syl)

        return urep

pre_save.connect(RecordedSyllable.set_md5hex, sender=RecordedSyllable)
