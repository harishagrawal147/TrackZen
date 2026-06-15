from urllib import request

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login ,logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from datetime import date, timedelta
from django.contrib import messages
from .utils import update_user_streak  
from django.utils import timezone
from django.contrib.auth import get_user_model
from django import forms
from .models import Points, UserBadge, Streak, Leaderboard, Feedback, DailyTask
from .services import calculate_leaderboard, get_user_streak, update_streak 

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User   
        fields = ("username", "email")
        

@login_required
def dashboard_view(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect("admin_dashboard")
    else:
        return redirect("student_dashboard")

@login_required
def admin_dashboard_view(request):
    if not request.user.is_staff:   
        return redirect("student_dashboard_view")
    
    today = timezone.now().date()

    students = User.objects.filter(is_staff=False)

    badges_awarded = UserBadge.objects.select_related("user", "badge").all()

    feedback_list = Feedback.objects.filter(created_at__date=today).order_by("-created_at")

    leaderboard = Points.objects.select_related("user").order_by("-total_points")[:10]

    return render(request, "TrackZen/admin_dashboard.html", {
        "students": students,
        "badges_awarded": badges_awarded,
        "feedback_list": feedback_list,
        "leaderboard": leaderboard
    })


@login_required
def student_dashboard_view(request):
    today = timezone.localtime(timezone.now()).date()

    if request.method == "POST":
        new_task = request.POST.get("new_task")
        task_id = request.POST.get("task_id")
        delete_task = request.POST.get("delete_task")   
        message = request.POST.get("message")

        # Feedback submission
        if message and message.strip():
            Feedback.objects.create(user=request.user, message=message.strip())
            messages.success(request, "Your feedback has been submitted successfully!")

        # Add new task
        if new_task and new_task.strip():   
            DailyTask.objects.create(
                user=request.user,
                task_name=new_task.strip(),
                is_completed=False,
                created_at=timezone.localtime(timezone.now()).date()
            )

            messages.success(request, f"Task '{new_task}' added for today!")
            return redirect("student_dashboard")

        # Mark task completed
        if task_id:
            try:
                task = DailyTask.objects.get(id=task_id, user=request.user)
                if not task.is_completed:
                    task.is_completed = True
                    task.save()

                    points, _ = Points.objects.get_or_create(user=request.user)
                    points.total_points += 10
                    points.save()

                    messages.success(request, f"Task '{task.task_name}' marked completed! You earned 10 points.")
            except DailyTask.DoesNotExist:
                messages.error(request, "Task not found or not valid for today.")

        # Delete task
        if delete_task:
            DailyTask.objects.filter(id=delete_task, user=request.user).delete()
            messages.success(request, "Task deleted successfully!")

        return redirect("student_dashboard")

    # Context data
    feedback_list = Feedback.objects.filter(user=request.user).order_by("-created_at")[:10]
    streak, _ = Streak.objects.get_or_create(user=request.user)
    tasks_today = DailyTask.objects.filter(user=request.user, created_at=today)
    tasks_history = DailyTask.objects.filter(user=request.user).exclude(created_at=today).order_by("-created_at")[:20]
    points, _ = Points.objects.get_or_create(user=request.user)
    top_students = Points.objects.order_by("-total_points")[:10]
    badges = UserBadge.objects.filter(user=request.user).select_related("badge")

    return render(request, "TrackZen/student_dashboard.html", {
        "feedback_list": feedback_list,
        "streak": streak,
        "tasks_today": tasks_today,
        "tasks_history": tasks_history,
        "points": points,
        "top_students": top_students,
        "badges": [ub.badge for ub in badges],
    })


@login_required
def dashboard_redirect(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("admin_dashboard")
        else:
            return redirect("student_dashboard")
    return redirect("login")


@login_required
def students_overview_view(request):
    students = Points.objects.select_related("user").order_by("-total_points")
    return render(request, "TrackZen/students_overview.html", {"students": students})



@login_required
def leaderboard_view(request):
    top_students = Points.objects.order_by("-total_points")
    return render(request, "TrackZen/admin_leaderboard.html", {"top_students": top_students})


@login_required
def student_leaderboard_view(request):
    top_students = Points.objects.select_related("user").order_by("-total_points")[:10]
    return render(request, "TrackZen/student_leaderboard.html", {"top_students": top_students})



@login_required
def badges_view(request):
    awarded_badges = UserBadge.objects.select_related("user").order_by("-awarded_at")[:10]
    return render(request, "TrackZen/badges.html", {
        "awarded_badges": awarded_badges
    })
    

@login_required
def student_badges_view(request):
    my_badges = UserBadge.objects.filter(user=request.user).order_by("-awarded_at")
    return render(request, "TrackZen/student_badges.html", {
        "my_badges": my_badges
    })



@login_required
def streak_view(request):
    streak, created = Streak.objects.get_or_create(
        user=request.user,
        defaults={"last_active_date": date.today()}
    )

    if not created and streak.last_active_date is None:
        streak.last_active_date = date.today()
        streak.save()

    streak_count = update_streak(request.user)

    return render(request, "TrackZen/streak.html", {
        "streak": streak,
        "streak_count": streak_count
    })


    
@login_required
def student_feedback_view(request):
    if request.method == "POST":
        if "delete_feedback" in request.POST:
            fb_id = request.POST.get("delete_feedback")
            Feedback.objects.filter(id=fb_id, user=request.user).delete()

    my_feedbacks = Feedback.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "TrackZen/student_feedback.html", {"my_feedbacks": my_feedbacks})
    
    
@login_required
def admin_feedback_view(request):
    today = timezone.localtime(timezone.now()).date()
    feedback_list = Feedback.objects.select_related("user").filter(created_at__date=today).order_by("-created_at")
    return render(request, "TrackZen/admin_feedback.html", {"feedback_list": feedback_list})
    
    
@login_required
def submit_feedback_view(request):
    feedback_list = Feedback.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "TrackZen/feedback.html", {
        "feedback_list": feedback_list,
    })

@login_required
def delete_feedback(request, pk):
    fb = get_object_or_404(Feedback, pk=pk)
    fb.delete()
    return redirect("admin_feedback") 

@login_required
def points_view(request):
    points_history = Points.objects.filter(user=request.user).order_by("created_at")
    points_data = [p.total_points for p in points_history]
    points_labels = [p.created_at.strftime("%d-%b") for p in points_history]
    total_points = sum(points_data) if points_data else 0
    return render(request, "TrackZen/points.html", {
        "points_labels": points_labels,
        "points_data": points_data,
        "total_points": total_points
    })
    

@login_required
def custom_login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("dashboard")  
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


@login_required
def custom_logout_view(request):
    logout(request)
    return redirect("login")


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = request.POST.get("email")
            user.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def delete_account_view(request):
    user = request.user
    user.delete()   
    messages.success(request, "Your account has been deleted successfully.")
    return redirect("login")


@login_required
def mark_task_completed(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id, user=request.user)
    if not task.is_completed:
        task.is_completed = True
        task.save()   

        points, created = Points.objects.get_or_create(user=task.user)
        points.total_points += 10
        points.save()

    return render(request, "TrackZen/task_complete.html", {"task": task})


        
@login_required
def task_history_view(request):
    today = timezone.localtime(timezone.now()).date()
    seven_days_ago = today - timedelta(days=7)


    tasks = DailyTask.objects.filter(
        user=request.user,
        created_at__gte=seven_days_ago
    ).order_by("-created_at")

    tasks_by_date = {}
    for task in tasks:
        tasks_by_date.setdefault(task.created_at, []).append(task)

    return render(request, "TrackZen/task_history.html", {
        "tasks_by_date": tasks_by_date,
    })
