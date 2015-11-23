import json
import math
from random import random
from itertools import count

from .models import Exam, Question, Answer, ExamRegister, AnswerRegister
from .enums import QuestionType


class ExamBuilder:
    """Draws the random questions to the new exam.

    Probability of drawing each question is based on the user rating and the
    question score.
    Each question is assigned a weight which is calculated as:
        w = 2 ** (-d*d)
    where
        d = (rating - score) / SCORE_DIFFERENCE
    Effectively, questions which score differs from student's rating by
    SCORE_DIFFERENCE has 50% less chance to be drawn than if they had the same
    score as the rating.

    Attributes:
      exam (Exam): exam which it chooses questions to
      peak (int): the score where the most questions are drawn (user rating)
      difficulty (int): difficulty of the questions set
    """

    # rating difference where probability of picking the question is halved
    SCORE_DIFFERENCE = 300

    def __init__(self, exam_id):
        self.exam = Exam.objects.prefetch_related(
            'question_set'
        ).get(
            id=exam_id
        )

    def set_rating(self, rating):
        """Sets the location of the score peak"""
        self.peak = rating

    def set_difficulty(self, difficulty):
        """Sets the difficulty of the question set.
        Difficulty determines the amount of questions drawn from each side of
        the main rating.
        """
        self.difficulty = difficulty
        raise NotImplementedError("Difficulty cannot be set")

    def draw_questions(self):
        """Returns the list of questions chosen according to their score."""
        questions = self.exam.question_set.all()
        amount = self.exam.num_questions
        weights, weight_sum = self.get_weights(questions)
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

    def get_weights(self, questions):
        """Returns the list of weights for each question and their sum."""
        weights = []
        sum = 0
        for question in questions:
            rating = question.rating
            diff = (rating - self.peak) / self.SCORE_DIFFERENCE
            weight = 2 ** (-diff * diff)
            weights.append(weight)
            sum += weight
        return (weights, sum)


class ScoreCalculator:
    """Calculator of the score gained for the answers.

    It calculates a score, expected score and the change in the rating for
    given answer to the question. Calculations are based on the elo rating
    system with small modifications to constants.

    Expected score is taken from the logistic function with the steepnes
    STEEP. The gradient at the inflection point is STEEP / 4.
    When student's and question's ratings are the same, then the score the
    student is expected to reach is REF_SCORE. It corresponds to moving the
    logistic curve along the x-axis so it intersects the y-axis at REF_SCORE
    Equation: 1 / (1 + exp(-ax))

    Multiplier is applied to the score obtained above the expected score to
    find the user rating change.
    On average user gain MULTIPLIER * (1-REF_SCORE) points.
    """

    # the slope of the curve at the inflection point is a = STEEP / 4
    STEEP = 0.01
    # the reference score, the rating won't change if achieved
    REF_SCORE = 0.7
    # difference between max score gain and max score lose
    MULTIPLIER = 50

    def get_answer_score(self, question, answer):
        """Calculates the score student get for the answer.

        Arguments:
          question (Question): the question queryset with `answer_set`
          answer: the answer given by the user (type varies by question type)
        """
        correct_answers = question.answer_set.filter(is_correct=True).all()
        correct_answer_ids = set([ans.id for ans in correct_answers])
        if question.type == QuestionType.single_choice:
            answer_id = int(answer)
            return answer_id in correct_answer_ids

        elif question.type == QuestionType.multiple_choice:
            answer_ids = set(map(int, answer))
            # User starts with 1 point and each incorrect answer or missing
            # correct answer takes 0.5 points from his score
            score = 1 - (len(correct_answer_ids - answer_ids) +
                         len(answer_ids - correct_answer_ids)) / 2
            return score if score >= 0 else 0

        elif question.type == QuestionType.open_ended:
            return 1
            raise NotImplementedError(
                'Open ended question score cannot be calculated'
            )

        else:
            raise ValueError('Invalid question type {}'.format(question))

    def get_expected_score(self, user_rating, question_rating):
        """Returns the score user is expected to reach.

        Expected score is the score which won't affect the rating. It's
        calculated using the logistic function
        """
        A = self.REF_SCORE / (1 - self.REF_SCORE)
        diff = question_rating - user_rating
        return round(A / (A + math.exp(self.STEEP * diff)), 6)

    def get_rating_change(self, score, expected_score):
        """Returns the amount of ratig points for the answer"""
        return self.MULTIPLIER * (score - expected_score)


class ExamFinalizer:
    """Class managing the post-exam actions.
    Saves the finished exam to the log and checks answers where possible.

    Arguments:
        user (User): the user who took the exam
        exam_id (int): database id of the exam
        question_ids ([int]): the list of answered questions ids
        answers ([dict]): dicts with info about given answers
            {'question_id', 'question_type', 'answer'}
        practise (bool): whether the practise mode was enabled

    Attributes:
        user (User): user who took the exam
        exam_id (int): id of the test
        questions_queryset (Question): queryset with exam questions, answer_set
            is prefetched
        answers ([dict]): dicts with user's answers
        practise (bool): practise mode
        calculator (ScoreCalculator): the instance of the calculator
    """

    def __init__(self, user, exam_id, question_ids, answers, practise):
        self.user = user
        self.exam_id = exam_id
        self.questions_queryset = Question.objects.prefetch_related(
            'answer_set'
        ).filter(
            id__in=question_ids
        )
        self.answers = answers
        self.practise = practise
        self.calculator = ScoreCalculator()

    def save_exam(self):
        """Saves the answers and the exam log into the database"""
        exam_register = ExamRegister(
            user=self.user,
            exam_id=self.exam_id,
            user_rating=self.user.student.rating
        )
        exam_register.save()
        for raw_answer in self.answers:
            answer = self.parse_answer(
                raw_answer['question_type'], raw_answer['answer']
            )
            AnswerRegister(
                exam_attempt=exam_register,
                question_id=int(raw_answer['question_id']),
                answer=answer,
                graded=True
            ).save()

    def adjust_rating(self):
        """Checks the answers and adjusts question and user rating"""
        total_rating_change = 0
        for raw_answer in self.answers:
            question = self.questions_queryset.get(
                id=raw_answer['question_id']
            )
            answer = self.parse_answer(
                question.type, raw_answer['answer']
            )
            score = self.calculator.get_answer_score(question, answer)
            expected_score = self.calculator.get_expected_score(
                self.user.student.rating, question.rating
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

    def parse_answer(self, question_type, answer):
        """Parses the serialized answer according to the question type"""
        if question_type == QuestionType.single_choice:
            return int(answer)
        elif question_type == QuestionType.multiple_choice:
            return [int(a) for a in answer]
        elif question_type == QuestionType.open_ended:
            return answer
        else:
            raise ValueError("Invalid QuestionType")
