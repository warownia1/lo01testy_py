import csv
import random
from collections import namedtuple

import itertools

import math
from django.db import transaction

from app.models import Question, Exam


QuestionRawData = namedtuple(
    'QuestionRaw', ['text', 'type', 'rating', 'answers'])


class ExamUploader:
    """
    Parses the uploaded file with the exam data and uploads it to the database.
    provided file should be a csv file with the following rows:
        question, type, rating, answer1, score1, answer2, score2, ...
    """
    def __init__(self, name, num_questions):
        self._name = name
        self._num_questions = num_questions
        self._data = None

    def load_csv(self, file, has_headers=False):
        """
        Reads data rows from the specified file and validate them.
        
        :param file: csv file containing exam data
        :param has_headers: whether the file has header row
        :return: None
        """
        reader = csv.reader(file)
        if has_headers:
            next(reader)
        self._data = [self._validate_row(row) for row in reader]

    @staticmethod
    def _validate_row(row):
        """
        Checks if the row structure is valid and extracts data from it.
        
        :param row: list of values from csv file
        :return: tuple with parsed row data.
        """
        q_type = row[1]
        if q_type not in {c[0] for c in Question.TYPE_CHOICES}:
            raise ValueError("Invalid question type {}".format(q_type))
        answers = [(row[i], int(row[i + 1])) for i in range(3, len(row), 2)]
        return QuestionRawData(
            text=row[0],
            type=q_type,
            rating=int(row[2] or Question.DEFAULT_RATING),
            answers=answers
        )

    def save_to_db(self):
        """
        Saves the uploaded exam file to the database.
        
        :return: None
        """
        if self._data is None:
            raise ValueError("File not uploaded")
        if self._num_questions > len(self._data):
            raise ValueError("Not enough questions")
        with transaction.atomic():
            exam = Exam.objects.create(
                name=self._name, num_questions=self._num_questions
            )
            for record in self._data:
                question = exam.questions.create(
                    text=record.text, type=record.type, rating=record.rating
                )
                for ans in record.answers:
                    question.answers.create(
                        text=ans[0], is_correct=ans[1]
                    )


class RandomQuestion:

    TOLERANCE = 300  # score difference where weight drops by half

    @classmethod
    def get_choices(cls, questions, num, peak, difficulty=None):
        """
        Randomly draws ``num``questions from the iterable given in ``questions``
        using the gaussian distribution centered at rating given in ``peak``
        
        :param questions: list of questions with their ratings
        :type questions: list[app.models.Question]
        :param int num: number of questions to randomly draw
        :param int peak: location of weight peak (middle rating)
        :param None difficulty: additional customization of difficulty
        :return: list of choices in the exam set
        :rtype: list[Question]
        """
        if difficulty is not None:
            raise NotImplementedError('Difficulty is not implemented yet')
        weights = cls.get_weights(questions, peak)
        total_cumulative = sum(weights)
        rand_questions = []
        while len(rand_questions) < num:
            rand = random.uniform(0, total_cumulative)
            cumulative = 0
            for (i, w) in zip(itertools.count(), weights):
                cumulative += w
                if cumulative > rand:
                    rand_questions.append(questions[i])
                    total_cumulative -= w
                    weights[i] = 0
                    break
        return rand_questions

    @classmethod
    def get_weights(cls, questions, peak):
        """
        Calculates a weight for each question based on its rating.
        
        :param questions: list of questions
        :type questions: collections.Iterable[app.models.Question]
        :param int peak: rating for which the weight is max
        :return: list of weight corresponding to questions
        :rtype: list[float]
        """
        return [
            2 ** (-((q.rating - peak) / cls.TOLERANCE) ** 2)
            for q in questions
        ]


class AnswerScore:

    ZERO_SCORE = 0.5  # score expected from the user for no rating difference
    SPAN = 200  # rating span where expected score is still near ZERO_SCORE
    MULTIPLIER = 100  # maximum rating change on a single question

    @classmethod
    def get_rating_change(cls, question, answer_choices, answer,
                          user_rating):
        """
        :param question: question for which it calculated the score
        :type question: Question
        :param answer_choices: query set of answer choices to this question
        :type answer_choices: 
            django.db.models.query.QuerySet[app.models.AnswerChoice]
        :param answer: id of list of ids of the answer given by the user
        :type answer: int | list[int]
        :param int user_rating: rating of the user who answered the question
        """
        score = cls.get_score(question, answer_choices, answer)
        expected = cls.get_expected_score(question, user_rating)
        print('score:', score, 'expected:', expected)
        return cls.MULTIPLIER * (score - expected)

    @staticmethod
    def get_score(question, answer_choices, answer):
        """
        :param Question question: answered question
        :param answer_choices: query set of answer choices
        :type answer_choices:
            django.db.models.query.QuerySet[app.models.AnswerChoice]
        :param answer: id or list of ids of the answer
        :type answer: int | list[int]
        :return: score obtained by the user for the answer
        :rtype: float
        """
        correct_answers = answer_choices.filter(is_correct=True)
        correct = {ans.id for ans in correct_answers}
        print('correct: %r' % correct)
        print('answer: %r' % answer)
        if question.type == Question.MULTIPLE_CHOICE:
            extra = len(answer) - len(correct.intersection(answer))
            missed = len(correct.difference(answer))
            score = 1 - (extra + missed) / 2
            return score if score >= 0 else 0
        elif question.type == Question.SINGLE_CHOICE:
            return int(answer in correct)
        else:
            raise AssertionError("Invalid question type '%s'" % question.type)

    @classmethod
    def get_expected_score(cls, question, user_rating):
        """
        Calculates a score that users with given rating should get on average.
        It compares relative user and question rating to determine the 
        expected result.
        
        :param Question question: question for which score is calculated
        :param int user_rating: rating of the user
        """
        a = cls.ZERO_SCORE / (1 - cls.ZERO_SCORE)
        diff = question.rating - user_rating
        expected = a / (a + math.exp(diff / cls.SPAN))
        return round(expected, 3)
