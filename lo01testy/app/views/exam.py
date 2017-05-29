from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from app.exam_tools import RandomQuestion, AnswerScore
from app.forms import ExamCodeForm, QuestionForm
from app.models import Exam, Question


@login_required
def exams_list_view(request):
    """
    Displays the list of exams add currently available to the user.
    
    name: exam:list
    URL: /exam/list/
    """
    today = timezone.now().date()
    user_id = request.user.id

    # Future exams sorted by the closest due date
    exams = (Exam.objects
             .filter(group__members__id=user_id)
             .filter(groupexamlink__due_date__gte=today)
             .annotate(closest_due_date=Min('groupexamlink__due_date'))
             .order_by('closest_due_date'))
    old_exams = (Exam.objects
                 .filter(group__members__id=user_id)
                 .filter(groupexamlink__due_date__lt=today)
                 .annotate(closest_due_date=Max('groupexamlink__due_date'))
                 .exclude(groupexamlink__due_date__gte=today)
                 .order_by('-closest_due_date'))
    return render(
        request, 'exam/list.html',
        {'exams': exams, 'old_exams': old_exams}
    )


@login_required
def exam_info_view(request, exam_id):
    """
    Show the information about the exam before user can start it.
    
    name: exam:info
    URL: /exam/info/<exam_id>
    """
    queryset = (Exam.objects
                .prefetch_related('groupexamlink_set__group')
                .prefetch_related('groupexamlink_set__group'))
    exam = get_object_or_404(queryset, id=exam_id)
    group_exam_links = exam.groupexamlink_set.order_by('-due_date').all()
    return render(
        request, 'exam/info.html',
        {'exam': exam, 'assigns': group_exam_links}
    )


@login_required
def exam_start_view(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    form = ExamCodeForm(request.POST or None, exam=exam)
    if form.is_valid():
        exam = (Exam.objects.prefetch_related('questions')
                            .get(id=exam_id))
        questions = RandomQuestion.get_choices(
            questions=exam.questions.all(),
            num=exam.num_questions,
            peak=request.user.userx.rating
        )
        request.session['exam_id'] = exam.id
        request.session['current_question'] = 0
        request.session['questions'] = [q.id for q in questions]
        return redirect('exam:question')
    return render(
        request, 'exam/enter_code.html',
        {'exam': exam, 'form': form}
    )


@login_required
def question_view(request):
    """
    Shows a next question to the user and manages the answers.
    Checks for an ongoing exam and picks a question from the list.
    Answers are checked and user's score is adjusted accordingly.
    
    name: exam:question
    URL: /exam/question/
    """
    exam_id = request.session.get('exam_id')
    if exam_id is None:
        return redirect('exam:list')
    exam = Exam.objects.get(id=exam_id)
    question_id = (
        request.session['questions'][request.session['current_question']]
    )
    question = Question.objects.get(id=question_id)
    answers = question.answers.all()
    form = QuestionForm(
        request.POST or None,
        question_type=question.type,
        answer_choices=[(ans.id, ans.text) for ans in answers]
    )
    if form.is_valid():
        score_change = AnswerScore.get_rating_change(
            question=question,
            answer_choices=answers,
            answer=form.cleaned_data['answer'],
            user_rating=request.user.userx.rating
        )
        request.user.userx.rating += score_change
        question.rating -= score_change
        request.user.userx.save()
        question.save()
        request.session['current_question'] += 1
        if request.session['current_question'] >= exam.num_questions:
            return redirect('exam:finished')
        else:
            return redirect('exam:question')
    return render(
        request, 'exam/question.html',
        {
            'exam_name': exam.name,
            'question': question, 'form': form,
            'question_no': request.session['current_question'],
            'num_questions': exam.num_questions
        }
    )


@login_required
def finished_view(request):
    return redirect('exam:list')