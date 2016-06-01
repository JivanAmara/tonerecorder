from django.core.management.base import BaseCommand
from tonerecorder.file_samples import load_all

class Command(BaseCommand):
    help = 'Adds users and RecordedSyllable instances to the database based on the archive'\
           ' directory specified.  This command is paired with dump_archive.'

    def add_arguments(self, parser):
        parser.add_argument('archive_directory')

    def handle(self, *args, **kwargs):
        directory = kwargs['archive_directory']
        load_all(directory)
