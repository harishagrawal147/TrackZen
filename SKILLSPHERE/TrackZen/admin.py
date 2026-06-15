from django.contrib import admin
from .models import Points, Badge, UserBadge, Streak, Leaderboard, Feedback

admin.site.register(Points)
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(Streak)
admin.site.register(Leaderboard)
admin.site.register(Feedback)