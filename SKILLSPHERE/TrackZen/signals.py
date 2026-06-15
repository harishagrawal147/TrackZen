from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now 
from .utils import update_user_streak 
from .models import Badge, UserBadge, Feedback, DailyTask

DAILY_BADGE = {"name": "Daily Achiever", "description": "Completed all tasks for the day"}


@receiver(post_save, sender=Feedback)
def update_streak_on_feedback(sender, instance, created, **kwargs):
    if created:
        update_user_streak(instance.user)


@receiver(post_save, sender=DailyTask)
def assign_daily_badge_on_task_complete(sender, instance, created, **kwargs):
    if instance.is_completed:
        today = timezone.localtime(timezone.now()).date()

        # Get all tasks for today (after deletes)
        tasks_today = DailyTask.objects.filter(user=instance.user, created_at=today)

        print("Tasks today:", tasks_today.count(), "All completed:", all(t.is_completed for t in tasks_today))

        # Award badge only if ALL remaining tasks are completed
        if tasks_today.exists() and all(t.is_completed for t in tasks_today):
            badge, _ = Badge.objects.get_or_create(
                name=DAILY_BADGE["name"],
                defaults={"description": DAILY_BADGE["description"]}
            )
            if not UserBadge.objects.filter(user=instance.user, badge=badge, awarded_at__date=today).exists():
                UserBadge.objects.create(user=instance.user, badge=badge)
                print("✅ Badge awarded to", instance.user)