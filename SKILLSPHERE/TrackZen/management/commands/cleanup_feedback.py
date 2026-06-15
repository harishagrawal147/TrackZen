from django.core.management.base import BaseCommand
from django.utils import timezone
from TrackZen.models import Feedback

class Command(BaseCommand):
    help = "Delete feedback older than today"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        deleted_count, _ = Feedback.objects.exclude(created_at__date=today).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} old feedback entries"))