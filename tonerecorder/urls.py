from django.conf.urls import url
from tonerecorder.views import MobileRecordView, AudioUploadView, AudioListenView
from django.contrib.auth.decorators import login_required

logged_in_mobile_record = login_required(MobileRecordView.as_view())
logged_in_audio_upload = login_required(AudioUploadView.as_view())
logged_in_audio_listen = login_required(AudioListenView.as_view())

urlpatterns = (
    url(r'record-mobile', logged_in_mobile_record, name='tonerecorder_record-mobile'),
    url(r'upload-audio', logged_in_audio_upload, name='tonerecorder_upload-audio'),
    url(r'listen-audio/(?P<rs_id>\d+)', logged_in_audio_listen, name='tonerecorder_listen-audio')
)
