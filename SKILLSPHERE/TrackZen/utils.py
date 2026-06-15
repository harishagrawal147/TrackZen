from django.utils.timezone import now
from .models import Streak

def update_user_streak(user):
    streak, _ = Streak.objects.get_or_create(user=user)
    today = now().date()

    if streak.last_active_date == today:
        # Already updated today → streak will remain same
        pass
    elif streak.last_active_date and (today.toordinal() - streak.last_active_date.toordinal() == 1):
        # Given feedback yesterday → streak +1
        streak.current_streak += 1
    else:
        # If there's a gap in activity → streak reset
        streak.current_streak = 1

    # Longest streak update
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak

    streak.last_active_date = today
    streak.save()
    return streak



def add_points(user, amount):
    from .models import Points
    points, created = Points.objects.get_or_create(user=user)
    points.total_points += amount
    points.save()
    return points.total_points

def generate_feedback(user):
    from .models import Feedback
    latest = Feedback.objects.filter(user=user).order_by("-created_at").first()
    if latest:
        return f"Your latest feedback: {latest.message}"
    return "You have not submitted any feedback yet."