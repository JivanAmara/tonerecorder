'''
Created on Mar 16, 2016

@author: jivan
'''
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from hanzi_basics.models import PinyinSyllable
from django.conf import settings
import os

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
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    syllable = models.ForeignKey(PinyinSyllable)

    # Full path to original audio
    audio_original = models.CharField(max_length=200, null=True)
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
                'original', 'wav', 'volume_normalized', 'silence_stripped'.
        '''
        pipeline_states = ['original', 'wav', 'volume_normalized', 'silence_stripped']
        if audio_version not in pipeline_states:
            raise(Exception('{} not a recognized audio sample state'.format(audio_version)))
        pipeline_index = pipeline_states.index(audio_version)
        file_extension = self.file_extension if pipeline_index == 0 else 'wav'
        filename = '{speaker}--{sound}--{tone}--{index}.{audio_version}.{extension}'.format(
                        speaker=self.user.username,
                        sound=self.syllable.sound,
                        tone=self.syllable.tone,
                        index=pipeline_index,
                        audio_version=audio_version,
                        extension=file_extension
                        )

        os.makedirs(os.path.join(settings.MEDIA_ROOT, settings.SYLLABLE_AUDIO_DIR), exist_ok=True)
        audio_path = os.path.join(settings.MEDIA_ROOT, settings.SYLLABLE_AUDIO_DIR, filename)
        return audio_path

    def __str__(self):
        u_syl = "{}".format(self.syllable)

        urep = "{0}: {1}"\
                   .format(self.user.username, u_syl)

        return urep

    class Meta:
        unique_together = ('user', 'syllable')

def create_audio_path(rs, audio_version):
    ''' *rs* is a RecordedSyllable instance
        *audio_version* should be one of:
            'original', 'wav', 'volume_normalized', 'silence_stripped'.
    '''
    pipeline_states = ['original', 'wav', 'volume_normalized', 'silence_stripped']
    if audio_version not in pipeline_states:
        raise(Exception('{} not a recognized audio sample state'.format(audio_version)))
    pipeline_index = pipeline_states.index(audio_version)
    file_extension = rs.file_extension if pipeline_index == 0 else 'wav'
    filename = '{speaker}--{sound}--{tone}--{index}--{audio_version}.{extension}'.format(
                    speaker=rs.user.username,
                    sound=rs.syllable.sound,
                    tone=rs.syllable.tone,
                    index=pipeline_index,
                    audio_version=audio_version,
                    extension=file_extension
                    )

    os.makedirs(os.path.join(settings.MEDIA_ROOT, settings.SYLLABLE_AUDIO_DIR), exist_ok=True)
    audio_path = os.path.join(settings.MEDIA_ROOT, settings.SYLLABLE_AUDIO_DIR, filename)
    return audio_path
