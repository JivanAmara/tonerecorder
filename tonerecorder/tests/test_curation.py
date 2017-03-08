import itertools

from django.contrib.auth.models import User
from hanzi_basics.models import PinyinSyllable
import pytest

from tonerecorder.file_samples import remove_nonexistent_paths, remove_empty_recordedsyllables
from tonerecorder.models import RecordedSyllable


# All paths for these RecordedSyllables are set up to be dangling
all_dangling = []
# Only the audo_wav path for these RecordedSyllables is set up to be dangling
wav_dangling = []
# None of the paths for these RecordedSyllables are dangling
no_dangling = []

def create_test_records():
    """ Creates 9 RecordedSyllable instances, 3 with all paths dangling,
        3 with audio_wav dangling, 3 with no paths dangling.
    """
    user = User.objects.create(username='testuser')
    nonexistent_wav_path = '/tmp/nonexistent.wav'
    valid_wav_path = '/tmp/valid.wav'
    open(valid_wav_path, 'a').close()

    # Create recorded syllable objects with all dangling paths
    for sound in ['ba', 'wo', 'jie']:
        syllable = PinyinSyllable.objects.create(sound=sound, tone=1)
        rs = RecordedSyllable.objects.create(user=user, syllable=syllable,
            # a real md5 isn't needed, esp for nonexistent files.  Just make it unique
            original_md5hex='{}-{}'.format(sound, 1),
            audio_original=nonexistent_wav_path,
            audio_wav=nonexistent_wav_path,
            audio_normalized_volume=nonexistent_wav_path,
            audio_silence_stripped=nonexistent_wav_path,
        )
        all_dangling.append(rs)

    # Create recorded syllable objects with only audio_wav dangling
    for sound in ['ba', 'wo', 'jie']:
        syllable = PinyinSyllable.objects.create(sound=sound, tone=2)
        rs = RecordedSyllable.objects.create(user=user, syllable=syllable,
            # a real md5 isn't needed, esp for nonexistent files.  Just make it unique
            original_md5hex='{}-{}'.format(sound, 2),
            audio_original=valid_wav_path,
            audio_wav=nonexistent_wav_path,
            audio_normalized_volume=valid_wav_path,
            audio_silence_stripped=valid_wav_path,
        )
        wav_dangling.append(rs)

    # Create recorded syllable objects with no dangling paths
    for sound in ['ba', 'wo', 'jie']:
        syllable = PinyinSyllable.objects.create(sound=sound, tone=3)
        rs = RecordedSyllable.objects.create(user=user, syllable=syllable,
            # a real md5 isn't needed, esp for nonexistent files.  Just make it unique
            original_md5hex='{}-{}'.format(sound, 3),
            audio_original=valid_wav_path,
            audio_wav=valid_wav_path,
            audio_normalized_volume=valid_wav_path,
            audio_silence_stripped=valid_wav_path,
        )
        no_dangling.append(rs)


@pytest.mark.django_db
def test_remove_nonexistent_paths():
    create_test_records()
    # create_test_records() should have created 9 RecordedSyllable instances
    assert RecordedSyllable.objects.count() == 9

    for rs in itertools.chain(all_dangling, wav_dangling, no_dangling):
        assert rs.audio_original is not None
        assert rs.audio_wav is not None
        assert rs.audio_normalized_volume is not None
        assert rs.audio_silence_stripped is not None

    remove_nonexistent_paths()

    for rs in all_dangling:
        rs.refresh_from_db()
        assert rs.audio_original is None
        assert rs.audio_wav is None
        assert rs.audio_normalized_volume is None
        assert rs.audio_silence_stripped is None

    for rs in wav_dangling:
        rs.refresh_from_db()
        assert rs.audio_original is not None
        assert rs.audio_wav is None
        assert rs.audio_normalized_volume is not None
        assert rs.audio_silence_stripped is not None

    for rs in no_dangling:
        rs.refresh_from_db()
        assert rs.audio_original is not None
        assert rs.audio_wav is not None
        assert rs.audio_normalized_volume is not None
        assert rs.audio_silence_stripped is not None

@pytest.mark.django_db
def test_remove_empty_recordedsyllables():
    """ Removes all RecordedSyllable instances with
        None values for audio_original, audio_wav, audio_normalized_volume, audio_silence_stripped
    """
    create_test_records()
    remove_nonexistent_paths()
    remove_empty_recordedsyllables()
    assert RecordedSyllable.objects.count() == 6
