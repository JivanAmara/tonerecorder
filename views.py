# coding=utf-8
from StringIO import StringIO
import json
import os
from random import randint
import random
import sys

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.views.generic import View

from hanzi_basics.models import PinyinSyllable
from tonerecorder.models import RecordedSyllable


AUDIOFILE_DIR = os.path.join(os.path.dirname(__file__), 'audio_files')

class MobileRecordView(View):
    def get(self, request):
        """ | *note*: Presumes an authenticated user, decorate with 'login_required'.
        """
        syllable = get_unrecorded_syllable(request.user)
        resp = render(request, 'record-html5-mobile.html', context={'syllable': syllable})
        return resp

class AudioUploadView(View):
    def post(self, request):
        if len(request.FILES.items()) != 1:
            resp = HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            syllable_string = request.POST['syllable']
            sound = syllable_string[:-1]
            tone = syllable_string[-1]
            syllable = PinyinSyllable.objects.get(sound=sound, tone=tone)
            filetype, file = request.FILES.items()[0]
            assert(filetype == 'audio')

            if len(file.name.split('.')) < 2:
                file_extension = '?'
            else:
                file_extension = file.name.split('.')[-1]

            RecordedSyllable.objects.create(
                user=request.user,
                syllable=syllable,
                content=file.read(),
                file_extension=file_extension,
            )

            resp = HttpResponseRedirect(reverse('tonerecorder_record-mobile'))
        return resp


def get_unrecorded_syllable(user):
    """ @brief Returns the pinyin of a sound this user hasn't yet recorded.
    """
    rss = RecordedSyllable.objects.filter(user=user)
    already_recorded = [ rs.syllable for rs in rss ]

    prioritized_sounds = \
        PinyinSyllable.objects\
               .values('sound')\
               .annotate(total_use_count=Sum('hanzis__use_count'))\
               .order_by('-total_use_count')

    # Cycle through the highest priority sounds, then through the syllables for
    #    each sound checking for the first which hasn't been recorded.
    next_to_record = None
    for prioritized_sound in prioritized_sounds:
        if next_to_record: break
        pinyin_syllables = \
            PinyinSyllable.objects\
                .filter(sound=prioritized_sound['sound'])\
                .order_by('tone')
        for ps in pinyin_syllables:
            if ps not in already_recorded:
                next_to_record = ps
                break

    return next_to_record.display
