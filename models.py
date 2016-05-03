'''
Created on Mar 16, 2016

@author: jivan
'''
from django.db import models
from django.contrib.auth.models import User
from hanzi_basics.models import PinyinSyllable

class RecordedSyllable(models.Model):
    user = models.ForeignKey(User)
    syllable = models.ForeignKey(PinyinSyllable)
    content = models.BinaryField()
    content_as_wav = models.BinaryField(null=True)
    content_as_normalized_wav = models.BinaryField(null=True)
    file_extension = models.CharField(max_length=40)

    def __unicode__(self):
        u_syl = "{}".format(self.syllable)

        urep = "{0}: {1}"\
                   .format(self.user.username, u_syl)

        return urep

    class Meta:
        unique_together = ('user', 'syllable')
