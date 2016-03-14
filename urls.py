from django.conf.urls import url
from tonerecorder.views import MobileRecordView, AudioUploadView

urlpatterns = (
    url(r'record-mobile', MobileRecordView.as_view(), name='tonerecorder_record-mobile'),
    url(r'upload-wav', AudioUploadView.as_view(), name='tonerecorder_upload-wav'),
)
