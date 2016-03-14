# coding=utf-8
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

import sys
import random
import os
from django.views.generic import View
from django.http.response import HttpResponseRedirect

AUDIOFILE_DIR = os.path.join(os.path.dirname(__file__), 'audio_files')

class MobileRecordView(View):
    def get(self, request):
        context = RequestContext(request)
        resp = render(request, 'record-html5-mobile.html')
        return resp

class AudioUploadView(View):
    def post(self, request):
        if len(request.FILES.items()) != 1:
            resp = HttpResponseRedirect(request.META['HTTP_REFERER'])
        else:
            filename, file = request.FILES.items()[0]
            rint = random.randint(1, sys.maxint)
            new_filename = 'uploaded_file_' + str(rint) + '.wav'
            new_fullpath = os.path.join(
                               AUDIOFILE_DIR, new_filename
                           )
            destination = open(new_fullpath, 'wb+')
            for chunk in file.chunks():
                destination.write(chunk)
            destination.close()
            msg = 'Saved as "{}".  Go back to recording page with new syllable queue.'\
                      .format(new_fullpath)
            resp = HttpResponse(msg)

        return resp
