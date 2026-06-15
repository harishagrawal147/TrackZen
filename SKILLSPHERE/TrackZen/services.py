from django.db import models
from .models import Leaderboard, Points, Feedback, Streak
from django.utils import timezone

def calculate_leaderboard():
    users_points = Points.objects.values("user").annotate(total=models.Sum("points"))
    Leaderboard.objects.all().delete()
    rank = 1
    for entry in sorted(users_points, key=lambda x: x["total"], reverse=True):
        Leaderboard.objects.create(user_id=entry["user"], total_points=entry["total"], rank=rank)
        rank += 1
        

def get_user_streak(user):
    try:
        streak = Streak.objects.get(user=user)
        return streak
    except Streak.DoesNotExist:
        return None

def update_streak(user):
    streak, created = Streak.objects.get_or_create(user=user)
    today = timezone.now().date()
    if streak.last_active_date == today:
        return streak.streak_count
    elif streak.last_active_date == today - timezone.timedelta(days=1):
        streak.streak_count += 1
    else:
        streak.streak_count = 1
    streak.last_active_date = today
    streak.save()
    return streak.streak_count
