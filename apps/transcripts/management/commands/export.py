import errno
import json
import os

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from apps.transcripts.models import Mission

class Command(BaseCommand):
    help = """Export a cleaned transcript and basic metadata file for use in
Spacelog.

If a transcript name isn't passed, the default is TEC."""

    args = "<mission-short-name> <export-dir> [<transcript-name>]"

    def handle(self, *args, **kwargs):
        if len(args) < 2 or len(args) > 3:
            raise CommandError("Wrong number of arguments.")

        try:
            mission = Mission.objects.get(short_name=args[0])
        except ObjectDoesNotExist:
            raise CommandError("No such mission.")

        export_dir = args[1]
        self._mkdir(os.path.join(export_dir, "transcripts"))

        main_transcript = "TEC"
        if len(args) > 2:
            main_transcript = args[2]

        cleaners = set()
        with open(os.path.join(export_dir, "transcripts", main_transcript), "w") as f:
            for page in mission.pages.all():
                f.write("\tPage %d\n" % page.number)
                f.write("\tApproved? %s\n" % page.approved)
                f.write(page.text)
                f.write("\n")

                for revision in page.revisions.all():
                    cleaners.add(revision.by.name)

        cleaners = list(cleaners)
        cleaners.sort()
        upper_title, lower_title = mission.name.split(" ", 1)
        meta = {
            "name": mission.short_name.lower(),
            "incomplete": True,
            "subdomains": [mission.short_name.lower()],
            "copy": {
                "title": mission.name,
                "upper_title": upper_title,
                "lower_title": lower_title,
                "cleaners": cleaners,
            },
            "main_transcript": "%s/%s" % (mission.short_name.lower(), main_transcript),
            "utc_launch_time": mission.start.isoformat(),
        }
        with open(os.path.join(export_dir, "transcripts", "_meta"), "w") as f:
            f.write(json.dumps(meta, indent=4))
            f.write("\n")

    def _mkdir(self, path):
        try:
            os.makedirs(path)
        except OSError as err:
            if err.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise CommandError("Cannot create directory '%s'" % path)
