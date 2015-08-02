import datetime
import urllib.parse

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max

from .models import *
from .forms import ExamCodeForm, AnswerForm
from .utils import ExamBuilder, ExamFinalizer


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
    queryset = Exam.objects.prefetch_related(
        'assign_set'
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
            exam = Exam.objects.get(id=id)
            exam_builder = ExamBuilder(id)
            exam_builder.set_rating(request.user.student.rating)
            exam_builder.set_difficulty(0)
            question_ids = [q.id for q in exam_builder.draw_questions()]
            request.session['exam'] = {
                "id": id,
                "name": exam.name,
                "current_question": 0,
                "num_questions": len(question_ids),
                "questions": question_ids,
                "practise": False,
                "finished": False,
                "answers": []
            }
            return redirect('exam:question')
    else:
        form = ExamCodeForm()
    exam = get_object_or_404(Exam, id=id)
    return render(
        request, 'main_screen/enter_exam_code.html',
        {'exam': exam, 'form': form}
    )


@login_required
def question(request):
    exam = request.session.get('exam')
    if (not exam or exam['finished']):
        return redirect('exam:list')
    question = Question.objects.prefetch_related(
        'answer_set'
    ).get(
        id=exam['questions'][exam['current_question']]
    )
    answers_list = [(a.id, a.text) for a in question.answer_set.all()]
    if request.method == 'POST':
        form = AnswerForm(question.type, answers_list, request.POST)
        if form.is_valid():
            answer = {
                'question_id': question.id,
                'question_type': question.type,
                'answer': form.cleaned_data['answer']
            }
            # Consider making changes on local exam objects and then copy it
            # back to session.
            request.session['exam']['answers'].append(answer)
            request.session['exam']['current_question'] += 1
            request.session.modified = True
            if (request.session['exam']['current_question'] <
                    request.session['exam']['num_questions']):
                return redirect('exam:question')
            else:
                request.session['exam']['finished'] = True
                ef = ExamFinalizer(
                    request.user, exam['id'], exam['questions'],
                    request.session['exam']['answers'], exam['practise'])
                ef.save_exam()
                rating_change = ef.adjust_rating()
                redir =  redirect('exam:show_results')
                get_request = "?%s" % urllib.parse.urlencode(
                    {"change": rating_change})
                redir['Location'] += "?{}".format(
                    urllib.parse.urlencode({"change": rating_change}))
                return redir
    else:
        form = AnswerForm(question.type, answers_list)

    return render(
        request, 'main_screen/question.html',
        {
            'exam': exam,
            'question': question,
            'form': form
        }
    )


@login_required
def show_results(request):
    rating_change = request.GET.get("change")
    if rating_change is None:
        rating_change = 0
    rating = request.user.student.rating
    return render(
        request, 'main_screen/result_screen.html',
        {
            'change': int(rating_change),
            'rating': rating
        }
    )

