from django.conf.urls.defaults import *
from tonerecorder.views import hello_world, whatd_you_say
from tonerecorder.views import upload_file, handle_upload

import os

CODEBASE_DIR = os.path.dirname(__file__) \
    + '/listenup_20100910/listenup/codebase/'

urlpatterns = patterns('',
    (r'play', hello_world),
    (r'record', whatd_you_say),
    (r'codebase/(.*)', 'django.views.static.serve'
        , {'document_root': CODEBASE_DIR, 'show_indexes': True} ),
#    (r'^audio/(.*)', 'django.views.static.serve'
#        , {'document_root': AUDIOFILE_DIR, 'show_indexes': True} ),
    (r'upload/', upload_file),
    (r'handle_upload/$', handle_upload)

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
