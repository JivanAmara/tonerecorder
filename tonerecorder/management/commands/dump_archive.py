from django.core.management.base import BaseCommand
from tonerecorder.file_samples import dump_all

class Command(BaseCommand):
    help = 'Dumps users and RecordedSyllable instances from the database to an archive'\
           ' directory specified.  This command is paired with load_archive.'

    def add_arguments(self, parser):
        parser.add_argument('archive_directory')

    def handle(self, *args, **kwargs):
        directory = kwargs['archive_directory']
        dump_all(directory)
