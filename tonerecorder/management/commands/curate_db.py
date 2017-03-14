from django.core.management.base import BaseCommand
from tonerecorder.file_samples import curate_db

class Command(BaseCommand):
    help = 'Cleans up (including removal of) RecordedSyllable & User models.'

    def handle(self, *args, **kwargs):
        curate_db()
