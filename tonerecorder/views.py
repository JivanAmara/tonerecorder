# coding=utf-8
try:
    from cStringIO import StringIO
except:
    from io import StringIO
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
from tonerecorder.file_samples import content_filename
from tempfile import NamedTemporaryFile
from django.db.models.aggregates import Count
from django.utils.decorators import method_decorator

AUDIOFILE_DIR = os.path.join(os.path.dirname(__file__), 'audio_files')

class AudioListenView(View):
    def get(self, request, rs_id):
        """ | *brief*: Returns a file-like response with the original content of the
            |    RecordedSyllable referenced by *rs_id*.
        """
        rs = RecordedSyllable.objects.get(id=rs_id)
        fname = content_filename(rs)
        r = HttpResponse(rs.content, content_type='audio')
        r['Content-Disposition'] = 'attachment; filename="{}"'.format(fname)
        return r

class MobileRecordView(View):
    def get(self, request):
        """ | *note*: Presumes an authenticated user, decorate with 'login_required'.
        """
        if not request.user_agent.is_mobile:
            resp = HttpResponse('Please visit this page with a smartphone, a desktop browser'\
                             ' will not function properly.')
        else:
            syllable, rank = get_unrecorded_syllable(request.user)
            recorded_count = RecordedSyllable.objects.filter(user=request.user).count()
            if recorded_count >= 200:
                resp = HttpResponse("You've recorded enough, thank you.")
            else:
                context = {
                    'syllable': syllable.display,
                    'syllable_rank': rank,
                    'recorded_count': recorded_count
                }
                resp = render(request, 'record-html5-mobile.html', context=context)
        return resp

class AudioUploadView(View):
    def post(self, request):
        if len(request.FILES.items()) != 1:
            resp = HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            syllable_string = request.POST['syllable']
            syllable = PinyinSyllable.objects.get(display=syllable_string)
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


def syllable_priorities_by_id():
    """ Returns a dictionary keying a pinyin sound-tone string (like 'ni3') to an integer
            rank, with 1 as the highest rank.  The ranks are based on usage data for
            hanzis with this pronunciation.
    """
    prioritized_syllables = \
        PinyinSyllable.objects\
               .values('sound', 'tone', 'id')\
               .annotate(total_use_count=Sum('hanzis__use_count'))\
               .order_by('-total_use_count')

    priority_lookup = {}
    for i, ps in enumerate(prioritized_syllables, 1):
        priority_lookup[ps['id']] = i

    return priority_lookup

def get_unrecorded_syllable(user):
    """ @brief Returns the pinyin of a sound this user hasn't yet recorded, along with the
            priority of the syllable.
    """
    rss = RecordedSyllable.objects.filter(user=user)
    already_recorded = [ rs.syllable for rs in rss ]

    priorities = syllable_priorities_by_id()

    prioritized_syllables = \
        PinyinSyllable.objects\
               .annotate(total_use_count=Sum('hanzis__use_count'))\
               .order_by('-total_use_count')

    # Cycle through the highest priority sounds, then through the syllables for
    #    each sound checking for the first which hasn't been recorded.
    next_to_record = None
    for i, prioritized_syllable in enumerate(prioritized_syllables, 1):
        if priorities[prioritized_syllable.id] != i:
            print('Priority mismatch! {} != {}'.format(priorities[prioritized_syllable.id], i))
        if prioritized_syllable not in already_recorded:
            next_to_record = prioritized_syllable
            break

    return (next_to_record, i)

class RecordingCountPerUser(View):
    def get(self, request):
        rss = RecordedSyllable.objects.values('user__username')\
                .annotate(nrecordings=Count('user__username'))

        trs = []
        for rs in rss:
            tr = '<tr><td>{}</td><td>{}</td></tr>'.format(rs['user__username'], rs['nrecordings'])
            trs.append(tr)

        table = '<table>{}</table>'.format('\n'.join(trs))
        ret = HttpResponse(table)
        return ret

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)
