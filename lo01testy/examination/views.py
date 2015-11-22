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
    """Display the list of all current exams available to the user.

    name: exam:list
    URL: /exam/list/
    """
    today = datetime.date.today()
    user_id = request.user.id

    # Oncoming exams sorted by the closest due date
    exams = Exam.objects.filter(
        group__members__id=user_id  # exams linked to user's group
    ).filter(
        assign__due_date__gte=today  # with future due date
    ).annotate(
        closest_due_date=Min("assign__due_date")  # take only closest date
    ).order_by(
        "closest_due_date"  # sort exams by the closest due date
    )

    # Past exams sorted by the most recent past date
    old_exams = Exam.objects.filter(
        group__members__id=user_id  # filter by the user's group
    ).filter(
        assign__due_date__lt=today  # having past due date
    ).annotate(
        closest_due_date=Max("assign__due_date")  # the most recent date
    ).exclude(
        assign__due_date__gte=today  # remove those with future due date too
    ).order_by(
        "-closest_due_date"  # sort by the closest past date
    )
    return render(request, 'main_screen/exams_list.html',
                  {"exams": exams, "old_exams": old_exams})


@login_required
def exam_overview(request, id):
    """Shows the informations about the exam before user starts it.

    name: exam:overview
    URL: /exam/overview/<id>
    """
    queryset = Exam.objects.prefetch_related(
        'assign_set'
    ).prefetch_related('assign_set__group')
    exam = get_object_or_404(queryset, id=id)
    assigns = exam.assign_set.order_by('-due_date').all()
    return render(request, 'main_screen/exam_overview.html',
                  {"exam": exam, "assigns": assigns})


@login_required
def init_exam(request, id):
    """Asks for the exam code or training mode and initializes a new exam.

    When the student starts the exam it draws questions from the database and
    creates a new exam instance. Exam data is stored in the current session
    in the `exam` variable. Structure of the object:
    {
        "id": (int) <exam id>,
        "name": (string) <name of the exam>,
        "current_question": (int) <current question number>
        "questions": ([int]) list of questions id numbers
        "practise": (bool) whether the practise mode is enabled
        "finished": (bool) whether the exam is finished (prevents clicking back
            and taking the exam again)
        "answers": (dict) the list of answers given by a student
    }

    name: exam:init
    URL: /exam/init/<id>
    """
    if request.method == 'POST':
        form = ExamCodeForm(request.POST)
        form.exam_id = id
        if form.is_valid():
            exam = Exam.objects.get(id=id)
            exam_builder = ExamBuilder(id)
            exam_builder.set_rating(request.user.student.rating)
            exam_builder.set_difficulty(0)
            question_ids = [q.id for q in exam_builder.draw_questions()]
            # a good candidate for a named tuple
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
    """Shows the next question to the user, and manages the answers.

    Checks for an ongoing exam (redirect to exams list if none) and picks a
    question from the list.
    If there is an answer to the previous questions, saves it to the current
    exam instance and pass to the next question; otherwise, displays the
    question.

    name: exam:question
    URL: /exam/question/
    """
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
            # if the previous question form is valid save and pass further
            # another good candidate for a named tuple
            answer = {
                'question_id': question.id,
                'question_type': question.type,
                'answer': form.cleaned_data['answer']
            }
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
                redir['Location'] += "?{}".format(
                    urllib.parse.urlencode({"change": rating_change})
                )
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
def final_result(request):
    """Displays users rating and its change after the exam.

    name: exam:show_result
    URL: /exam/result/
    GET: change: rating change
    """
    rating_change = request.GET.get("change")
    if rating_change is None:
        rating_change = 0
    current_rating = request.user.student.rating
    return render(
        request, 'main_screen/result_screen.html',
        {
            'change': int(rating_change),
            'rating': current_rating
        }
    )
