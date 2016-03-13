from django.conf.urls import url

from tonerecorder.views import hello_world, whatd_you_say
from tonerecorder.views import handle_upload
from tonerecorder.views import makefile
import os

CODEBASE_DIR = os.path.dirname(__file__) \
    + '/listenup_20100910/listenup/codebase/'

urlpatterns = (
    url(r'makefile/(.*?)$', makefile),
    url(r'play', hello_world),
    url(r'record', whatd_you_say),
    url(r'codebase/(.*)', 'django.views.static.serve'
        , {'document_root': CODEBASE_DIR, 'show_indexes': True}),
#    url(r'^audio/(.*)', 'django.views.static.serve'
#        , {'document_root': AUDIOFILE_DIR, 'show_indexes': True} ),
    url(r'handle_upload', handle_upload)

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
