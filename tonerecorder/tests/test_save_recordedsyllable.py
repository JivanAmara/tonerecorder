import os
import pytest
from tonerecorder.models import RecordedSyllable
from hanzi_basics.models import PinyinSyllable

@pytest.mark.django_db
def test_save_generates_md5():
    audio_path = os.path.join(os.path.dirname(__file__), 'test_audio.mp3')
    # For this test, it doesn't really matter if the syllable referenced is accurate.
    s = PinyinSyllable.objects.first()
    rs = RecordedSyllable(syllable=s)
    rs.audio_original = audio_path
    rs.save()

    assert rs.original_md5hex == '2b6d60c04a7995df97229ba7289cf464'
