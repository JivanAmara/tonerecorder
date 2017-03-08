""" Checks correct extraction of metadata from file name.
"""
from django.contrib.auth.models import User
from hanzi_basics.models import PinyinSyllable
import pytest

from tonerecorder.file_samples import file_metadata, content_filenames
from tonerecorder.models import RecordedSyllable


valid_filenames = {
    # Note the case conversion of sound 'E' -> 'e'.
    'standardmandarin.com--E--4--3.silence_stripped.wav': {
        'pipeline_status_text': 'silence_stripped', 'tone': '4', 'sound': 'e',
        'extension': 'wav', 'pipeline_index': '3', 'speaker_name': 'standardmandarin.com'
    },
    # Note the lack of case conversion for username.
    'Hezel_Bella--hua--1--0.original.wma': {
        'pipeline_status_text': 'original', 'tone': '1', 'sound': 'hua',
        'extension': 'wma', 'pipeline_index': '0', 'speaker_name': 'Hezel_Bella'
    },
}

def test_file_metadata():
    for filename, expected_metadata in valid_filenames.items():
        metadata = file_metadata(filename)
        assert metadata == expected_metadata

def test_content_filenames():
    # --- Add test RecordingSyllable model instances.
    # Note the difference in case between the expected usernames and the filenames passed to RecordedSyllable()
    # Sound, tone, username
    test_rss_params = {
        ('ba', 1, 'user1'): {
                'original': 'user1--ba--1--0.original.mp3',
                'wav': 'user1--ba--1--1.wav.wav',
                'volume_normalized': 'user1--ba--1--2.volume_normalized.wav',
                'silence_stripped': 'user1--ba--1--3.silence_stripped.wav',
            },
        ('ting', 3, 'user1'): {
                'original': 'user1--ting--3--0.original.mp3',
                'wav': 'user1--ting--3--1.wav.wav',
                'volume_normalized': 'user1--ting--3--2.volume_normalized.wav',
                'silence_stripped': 'user1--ting--3--3.silence_stripped.wav',
            },
        ('jiao', 4, 'user2'): {
                'original': 'user2--jiao--4--0.original.mp3',
                'wav': 'user2--jiao--4--1.wav.wav',
                'volume_normalized': 'user2--jiao--4--2.volume_normalized.wav',
                'silence_stripped': 'user2--jiao--4--3.silence_stripped.wav',
            },
    }
    test_rss = []
    for (sound, tone, username), expected_filenames in test_rss_params.items():
        # No need for actual persistence, so create but don't save these models.
        user = User(username=username)
        ps = PinyinSyllable(sound=sound, tone=tone)
        rs = RecordedSyllable(
            user=user, syllable=ps, audio_original='Original.mp3', audio_wav='Wav.wav',
            audio_normalized_volume='Normalized_volume.wav', audio_silence_stripped='Silence_stripped.wav',
            original_md5hex='{}-{}-{}'.format(sound, tone, username)
        )
        test_rss.append((rs, expected_filenames))

    # --- Cycle through the test instances & check if the filenames produced are correct.
    for rs, expected_filenames in test_rss:
        filenames = content_filenames(rs)
        assert filenames == expected_filenames
