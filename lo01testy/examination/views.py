from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Min

from .models import Exam


@login_required
def exams_list(request):
    user_id = request.user.id
    exams = Exam.objects.filter(
        group__members__id=user_id
    ).annotate(
        closest_due_date=Min("assign__due_date")
    ).order_by("closest_due_date")
    
    return render(request, 'main_screen/exams_list.html', {"exams": exams})
