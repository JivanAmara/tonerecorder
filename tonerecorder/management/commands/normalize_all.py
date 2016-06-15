from django.core.management.base import BaseCommand
from tonerecorder.normalize_samples import normalize_all

class Command(BaseCommand):
    help = 'Performs all normalization procedures on all out-of-date RecordedSyllables.'

    def handle(self, *args, **kwargs):
        normalize_all()
