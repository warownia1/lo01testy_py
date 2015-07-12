import datetime
from pprint import pprint

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max

from .models import Exam


@login_required
def exams_list(request):
    today = datetime.date.today()
    user_id = request.user.id
    exams = Exam.objects.filter(
        group__members__id=user_id
    ).filter(
        assign__due_date__gte=today
    ).annotate(
        closest_due_date=Min("assign__due_date")
    ).order_by(
        "closest_due_date"
    )
    
    old_exams = Exam.objects.filter(
        group__members__id=user_id
    ).filter(
        assign__due_date__lt=today
    ).annotate(
        closest_due_date=Max("assign__due_date")
    ).exclude(
        assign__due_date__gte=today
    ).order_by(
        "-closest_due_date"
    )
    
    return render(request, 'main_screen/exams_list.html', 
        {"exams": exams, "old_exams": old_exams})

@login_required        
def show_exam(request, id):
    queryset = Exam.objects.prefetch_related('assign_set'
        ).prefetch_related('assign_set__group')
    exam = get_object_or_404(queryset, id=id)
    assigns = exam.assign_set.order_by('-due_date').all()
    return render(request, 'main_screen/show_exam.html', 
        {"exam": exam, "assigns": assigns})