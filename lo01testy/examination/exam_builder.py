from random import random
from itertools import count

from .models import Exam, Question

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
