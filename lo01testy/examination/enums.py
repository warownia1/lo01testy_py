class QuestionType:
    single_choice = 'S'
    multiple_choice = 'M'
    open_ended = 'O'

    @staticmethod
    def is_valid(type):
        return type in ('S', 'M', 'O')
