from django.core.management.base import BaseCommand
from django.db import models
import math

from apps.people.models import User


# Configure the decay rate. Times are in minutes.
# `FREQUENCY` should match the frequency of command invocation (typically
# via cron).
#
# Calculated thus:
#    DECAY_FACTOR ^ (HALF_LIFE / FREQUENCY) = 0.5
# => DECAY_FACTOR                           = 0.5 ^ (FREQUENCY / HALF_LIFE)
FREQUENCY = 5
HALF_LIFE = 14*24*60
DECAY_FACTOR = math.pow(0.5, float(FREQUENCY) / HALF_LIFE)


class Command(BaseCommand):
    help = """Decay people's scores; run this regularly."""

    def handle(self, *args, **options):
        User.objects.all().update(
            score=models.F('score') * DECAY_FACTOR,
        )
