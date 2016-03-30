from django.conf.urls import url
from tonerecorder.views import MobileRecordView, AudioUploadView
from django.contrib.auth.decorators import login_required

logged_in_mobile_record = login_required(MobileRecordView.as_view())
logged_in_audio_upload = login_required(AudioUploadView.as_view())

urlpatterns = (
    url(r'record-mobile', logged_in_mobile_record, name='tonerecorder_record-mobile'),
    url(r'upload-audio', logged_in_audio_upload, name='tonerecorder_upload-audio'),
)
