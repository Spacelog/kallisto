from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option
import os.path

from apps.transcripts.models import *


class Command(BaseCommand):
    help = """Import images and text for mission transcript pages.

To generate PNGs from a PDF (using huge amounts of memory):

  $ convert -density 300 <pdf-file> png/page-%03d.png

To generate text from a PDF:

  $ gs -dNOPAUSE -dBATCH -sDEVICE=txt -sOutputFile=text/page-%03d.txt <pdf-file>

or with ghostscript 9.18 (eg in homebrew):

  $ gs -dNOPAUSE -dBATCH -sDEVICE=txtwrite -sOutputFile=text/page-%03d.txt <pdf-file>

Note that PNGs will be 0-indexed where text is 1-indexed, because tool
consistency between ImageMagick and ghostscript would destroy the
universe."""
    option_list = BaseCommand.option_list + (
    )
    args = "<mission-short-name> <png-dir> <text-dir> [<start-page> [<end-page]]"

    def handle(self, *args, **options):
        verbosity = int(options['verbosity'])

        if len(args) < 3 or len(args) > 5:
            raise CommandError("Wrong number of arguments.")
        
        mission = Mission.objects.get(short_name=args[0])
        self.stdout.write(u"Importing for mission %s." % mission.name)
        
        png_dir = args[1]
        text_dir = args[2]
        page = 1
        end = None

        if len(args) > 3:
            page = int(args[3])
        if len(args) > 4:
            end = int(args[4])

        with transaction.atomic():
            # We don't os.listdir() because we need to know which page number
            # we're dealing with.
            #
            # Remember that PNGs are 0-indexed.
            while end is None or page < end:
                png_fname = os.path.join(png_dir, "page-%3.3i.png" % (page-1))
                text_fname = os.path.join(text_dir, "page-%3.3i.txt" % page)
                if not (
                    os.path.exists(png_fname) and os.path.exists(text_fname)
                ):
                    break

                self.stdout.write(u" * page %i\n" % page)
            
                with open(text_fname, 'r') as text_f:
                    text = text_f.read().decode('iso-8859-1')
                with open(png_fname, 'r') as png_f:
                    p = Page.objects.create(
                        mission = mission,
                        number = page,
                        original = File(png_f),
                        original_text = text,
                    )
                page += 1
