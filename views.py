# coding=utf-8
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import sys
import random
import os

AUDIOFILE_DIR = os.path.join(os.path.dirname(__file__), 'audio_files')

def hello_world(request):
    resp = HttpResponse(
               '<head></head>'
               '<body><h1>Hello World!!!</h1>'
                   '<applet '
                       'code="com.softsynth.javasonics.recplay.PlayerApplet"'
                       'codebase="/tonerecorder/codebase/"'
                       'archive="JavaSonicsListenUp.jar"'
                       'name="ListenUpPlayer"'
                       'width="400"'
                       'height="120">'
                       #<!-- Play immediately without waiting for button press. -->
                       '<param name="autoPlay" value="yes">'
                       #<!-- Play the file at this URL. -->
                       '<param name="sampleURL" value="/audio/welcome.wav">'
                   '</applet>'
               '</body>'
           )

    return resp

@login_required
def whatd_you_say(request):
    rc = RequestContext(request)
    resp = render_to_response('record.html', rc)

    return resp

@login_required
@csrf_exempt
def handle_upload(request):
    resp = "CALLJS alert('Server says Yo.');\n"
    resp += "CALLJS say_hi();\n"
    resp += "SUCCESS"
    print("Received POST.")
    print("Files in post: \n")
    print(request.FILES.keys())
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

    return HttpResponse(resp)

def handle_uploaded_file(up_file):
    print("Got it!")
    fullpath = os.path.join(AUDIOFILE_DIR, 'upload.wav')
    ondisk_file = open(fullpath, "wb")
    ondisk_file.write(up_file.read())
    ondisk_file.close()

def makefile(request, filename):
    fullpath = os.path.join(AUDIOFILE_DIR, filename)
    ondisk_file = open(fullpath, "wb")
    ondisk_file.write(str(random.randint(0, 254)))
    ondisk_file.close()
    return HttpResponse(fullpath)

#from django import forms
#class UploadFileForm(forms.Form):
#    title = forms.CharField(max_length=50)
#    file  = forms.FileField()

"""
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print("Number of files: {0}".format(len(request.FILES)))
        for filename in request.FILES.keys():
            print(filename)
            
#        if form.is_valid():
        handle_uploaded_file(request.FILES['userfile'])
        return HttpResponseRedirect(reverse(upload_file))
    else:
        form = UploadFileForm()
    return render_to_response('upload.html'
                              , {'form': form}
                              ,context_instance=RequestContext(request)
    )
"""
