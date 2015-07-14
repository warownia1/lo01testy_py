import datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max

from .models import Exam
from .forms import ExamCodeForm


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

@login_required
def start_exam(request, id):
    if request.method == 'POST':
        form = ExamCodeForm(request.POST)
        form.exam_id = id
        if form.is_valid():
            request.session['exam_id'] = id
            request.session['exam'] = {
                # Populate the dictionary-object with some fields
                # You may call a separate function to do this
            }
            return redirect('exam:question')
    else:
        form = ExamCodeForm()
    exam = get_object_or_404(Exam, id=id)
    return render(request, 'main_screen/enter_exam_code.html',
        {'exam': exam, 'form': form})

def question(request):
    return HttpResponse(request.session['questions']['first']['id'])
