import json
from random import random
from itertools import count

from .models import Exam, Question, Answer, ExamRegister, AnswerRegister
from .enums import QuestionType


class ExamBuilder:

    # rating difference where probability of picking that question is halved
    SCORE_DIFFERENCE = 300

    def __init__(self, exam_id):
        self.exam = Exam.objects.prefetch_related(
            'question_set'
        ).get(id=exam_id)
        return

    # Set the location of the peak where the most questions are drawn
    def set_rating(self, rating):
        self.peak = rating
        return

    # Sets the difficulty level for the question set.
    # Does not affect peak location but amount of question at each side of the peak.
    # Not implemented yet.
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        return

    # Takes the amount of questions to draw and returns Question objects
    def draw_questions(self):
        questions = self.exam.question_set.all()
        amount = self.exam.num_questions
        weight_sum = 0
        weights = []
        # iterates over questions and gets their weights
        for question in questions:
            rating = question.rating
            diff = (rating - self.peak) / self.SCORE_DIFFERENCE
            weight = pow(2, -diff*diff)
            weights.append(weight)
            weight_sum += weight
        result = []
        while amount:
            rand = weight_sum * random()
            threshold = 0
            for (i, w) in zip(count(), weights):
                threshold += w
                if threshold > rand:
                    result.append(questions[i])
                    weight_sum -= w
                    weights[i] = 0
                    break
            amount -= 1
        return result


class ScoreCalculator:

    # slope of the curve
    # the tangent line slope is -ln(a)/4
    SLOPE = 1.05
    # default score expected from the student to archieve
    EXPECTED_SCORE = 0.7
    # difference between max score gain and max score lose
    MULTIPLIER = 50

    # Takes a question queryset and the answer of the user.
    # Questyset should have prefetched answer_set.
    # In case of a single choice question, answer shall contain a number
    # In case of a multiple choice, answer shall contain a list of ids
    # Returns the score of the answer which is 1 for correct and 0 for incorrect
    def get_answer_score(self, question, answer):
        correct_answers = question.answer_set.filter(is_correct=True).all()
        correct_answer_ids = set([ans.id for ans in correct_answers])
        if question.type == QuestionType.single_choice:
            answer_id = int(answer)
            if answer_id in correct_answer_ids:
                return 1
            else:
                return 0

        elif question.type == QuestionType.multiple_choice:
            answer_ids = set([int(ans) for ans in answer])
            # ::: Method 2 :::
            # User starts with 1 point and each missing correct answer or
            # incorrect answer takes 0.5 points from his score
            score = 1 - (len(correct_answer_ids - answer_ids) +
                         len(answer_ids - correct_answer_ids)) / 2
            if score < 0:
                return 0
            else:
                return score
            # ::: Method 1 :::
            # Each correct or incorrect answer is worth 1/len(correct) points
            # Correct answers are added to the result and incorrect are subtracted
            gain = (len(correct_answer_ids) -
                    len(correct_answer_ids - answer_ids) -
                    len(answer_ids - correct_answer_ids))
            if gain < 0:
                return 0
            return gain / len(correct_answer_ids)

        elif question.type == QuestionType.open_ended:
            return 1
            raise NotImplementedError(
                'Open ended question score cannot be calculated'
            )

        else:
            raise ValueError('Invalid question type {}'.format(question))
        return

    # Returns the score expected from the user to achieve
    def get_expected_score(self, user_rating, question_rating):
        A = self.EXPECTED_SCORE / (1 - self.EXPECTED_SCORE)
        diff = question_rating - user_rating
        return round(A / (A + self.SLOPE ** diff), 6)

    def get_rating_change(self, score, expected_score):
        return self.MULTIPLIER * (score - expected_score)


class ExamFinalizer:

    def __init__(self, user, exam_id, question_ids, answers, practise):
        self.user = user
        self.exam_id = exam_id
        self.questions_queryset = Question.objects.prefetch_related(
            'answer_set'
        ).filter(
            id__in=question_ids
        )
        # answer is a dictionary {question_id, question_type, answer}
        self.answers = answers
        self.practise = practise
        self.calculator = ScoreCalculator()
        return

    def save_exam(self):
        exam_register = ExamRegister(
            user=self.user,
            exam_id=self.exam_id,
            user_rating=self.user.student.rating
        )
        exam_register.save()
        for raw_answer in self.answers:
            if raw_answer['question_type'] == QuestionType.single_choice:
                answer = int(raw_answer['answer'])
            elif raw_answer['question_type'] == QuestionType.multiple_choice:
                answer = [int(a) for a in raw_answer['answer']]
            elif raw_answer['question_type'] == QuestionType.open_ended:
                answer = raw_answer['answer']
            else:
                raise ValueError("Invalid QuestionType")
            AnswerRegister(
                exam_attempt=exam_register,
                question_id=int(raw_answer['question_id']),
                answer=answer,
                graded=True
            ).save()
        return

    def adjust_rating(self):
        total_rating_change = 0
        for raw_answer in self.answers:
            question = self.questions_queryset.get(
                id=raw_answer['question_id']
            )
            if question.type == QuestionType.single_choice:
                answer = int(raw_answer['answer'])
            elif question.type == QuestionType.multiple_choice:
                answer = [int(a) for a in raw_answer['answer']]
            else:
                answer = raw_answer['answer']
            score = self.calculator.get_answer_score(question, answer)
            expected_score = self.calculator.get_expected_score(
                self.user.student.rating,
                question.rating
            )
            rating_change = self.calculator.get_rating_change(
                score, expected_score
            )
            total_rating_change += rating_change
            question.rating -= int(round(rating_change))
            question.save()
        rounded_total_change = int(round(total_rating_change))
        self.user.student.rating += rounded_total_change
        self.user.student.save()
        return rounded_total_change
