from django import forms

from .models import ExamCode
from .enums import QuestionType


class ExamCodeForm(forms.Form):
    code = forms.CharField(
        label="Kod",
        max_length=10,
        error_messages={
            "required": "To pole jest wymagane",
            "max_length": "Maksymalna ilość znaków: 25",
        }
    )

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not ExamCode.objects.filter(
                    code=code
                ).filter(
                    exam_id=self.exam_id
                ).exists():
            raise forms.ValidationError(
                "Niewłaściwy kod",
                code='incorrect_code'
            )
        return code


class AnswerForm(forms.Form):
    # answers shall be a list of tuples [(answer_id, answer_text), ]
    def __init__(self, question_type, answers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if question_type == QuestionType.open_ended:
            self.fields['answer'] = forms.CharField(
                label="Odpowiedź",
                min_length=10,
                widget=forms.Textarea(
                    attrs={
                        'cols': 72,
                        'rows': 10,
                    }
                ),
                error_messages={
                    "required": "To pole jest wymagane",
                    "min_length": "Wprowadź przynajmniej 10 znaków",
                }
            )
        elif question_type == QuestionType.single_choice:
            self.fields['answer'] = forms.ChoiceField(
                label="Odpowiedź",
                choices=answers,
                widget=forms.RadioSelect(),
                error_messages={
                    "required": "Wybierz co najmniej jedną odpowiedź.",
                    "invalid_choice": "%(value)s nie jest jedną z "
                                      "dostępnych opcji."
                }
            )
        elif question_type == QuestionType.multiple_choice:
            self.fields['answer'] = forms.MultipleChoiceField(
                label="Odpowiedź",
                choices=answers,
                widget=forms.CheckboxSelectMultiple(),
                error_messages={
                    "required": "Wybierz co najmniej jedną odpowiedź.",
                    "invalid_choice": "%(value)s nie jest jedną z "
                                      "dostępnych opcji."
                }
            )
        else:
            raise ValueError(
                "{} is not a valid QuestionType".format(question_type)
            )
        return
