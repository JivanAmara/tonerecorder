'''
Created on Mar 16, 2016

@author: jivan
'''
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from hanzi_basics.models import PinyinSyllable


@python_2_unicode_compatible
class RecordedSyllable(models.Model):
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    syllable = models.ForeignKey(PinyinSyllable)
    content = models.BinaryField()
    content_as_wav = models.BinaryField(null=True)
    # Normalized Volume
    content_as_normalized_wav = models.BinaryField(null=True)
    # Silence Stripped version of content_as_normalized_wav
    content_as_silence_stripped_wav = models.BinaryField(null=True)
    file_extension = models.CharField(max_length=40)
    # This text is used to determine if normalization should be redone.
    normalize_version = models.CharField(max_length=10)

    def __str__(self):
        u_syl = "{}".format(self.syllable)

        urep = "{0}: {1}"\
                   .format(self.user.username, u_syl)

        return urep

    class Meta:
        unique_together = ('user', 'syllable')
