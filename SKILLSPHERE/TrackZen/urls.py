from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("dashboard-redirect/", views.dashboard_redirect, name="dashboard_redirect"),
    path("admin-dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("student-dashboard/", views.student_dashboard_view, name="student_dashboard"),

    path("complete-task/<int:task_id>/", views.mark_task_completed, name="mark_task_completed"),
    path("task-history/", views.task_history_view, name="task_history"),
    path("students-overview/", views.students_overview_view, name="students_overview"),

    path("leaderboard/", views.leaderboard_view, name="leaderboard_page"),
    path("student-leaderboard/", views.student_leaderboard_view, name="student_leaderboard"),

    path("badges/", views.badges_view, name="badges_page"),
    path("student-badges/", views.student_badges_view, name="student_badges_page"),

    path("streak/", views.streak_view, name="streak"),
    path("points/", views.points_view, name="points"),

    path("student-feedback/", views.student_feedback_view, name="student_feedback"),
    path("admin-feedback/", views.admin_feedback_view, name="admin_feedback"),
    path("feedback/submit/", views.submit_feedback_view, name="submit_feedback"),
    path("feedback/delete/<int:pk>/", views.delete_feedback, name="delete_feedback"),

    path("", views.signup_view, name="signup"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout_default"),
    path("logout/", views.custom_logout_view, name="logout"),
    path("delete-account/", views.delete_account_view, name="delete_account"),
]