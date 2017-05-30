import re

from django import forms
from django.contrib.auth.models import User

from app.models import ExamCode, RegistrationCode, Question


# Account creation and management forms

class LoginForm(forms.Form):
    """User sign-in form asking for username and password"""
    username = forms.CharField(
        label="Użytkownik",
        max_length=30,
        error_messages={
            "required": "To pole jest wymagane",
            "max_length": "Maksymalna ilość znaków: 25",
        }
    )
    password = forms.CharField(
        label="Hasło",
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane",
        }
    )


class RegistrationForm(forms.Form):
    """
    User sign-up form asking for new username, password and code.
    Form used to create new accounts, requires registration code to create one.
    """
    username = forms.CharField(
        label="Nazwa użytkownika",
        min_length=1,
        max_length=30,
        error_messages={
            "required": "To pole jest wymagane",
            "min_length": "Login jest zbyt krótki",
            "max_length": "Login nie może zawierać więcej niż 30 znaków"
        }
    )
    password = forms.CharField(
        label="Hasło",
        min_length=3,
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane",
            "min_length": "Hasło jest zbyt krótkie",
        }
    )
    password2 = forms.CharField(
        label="Powtórz hasło",
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane"
        }
    )
    code = forms.CharField(
        label="Kod rejestracji",
        error_messages={
            "required": "To pole jest wymagane"
        }
    )

    def clean_username(self):
        """
        Checks whether the username contains valid characters only and does not
        exist in the database yet.
        """
        username = self.cleaned_data.get('username')
        if re.search(r'[^\w@.\-]', username):
            raise forms.ValidationError(
                "Nazwa użytkownika zawiera niedozwolone znaki",
                code='illegal_char'
            )
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Uzytkownik już istnieje",
                code='username_exists'
            )
        return username

    def clean_password2(self):
        """Checks whether two passwords match each other."""
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError(
                'Hasła są różne',
                code='pass_not_match'
            )
        return password

    def clean_code(self):
        """Cheks whether the registration code is valid."""
        code = self.cleaned_data.get('code')
        code_queryset = RegistrationCode.objects.filter(code=code)
        if not code_queryset.exists():
            raise forms.ValidationError(
                "Niewłaściwy kod",
                code='invalid_code'
            )
        elif code_queryset[0].used:
            raise forms.ValidationError(
                "Kod został użyty",
                code="code_used"
            )
        return code


class ChangePasswordForm(forms.Form):
    """
    Form used for user's password changing.
    Checks whether the old and new passwords match.
    """
    # TODO add __init__ accepting current user for old password validation
    old_password = forms.CharField(
        label="Stare hasło",
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane",
        }
    )
    new_password = forms.CharField(
        label="Nowe hasło",
        min_length=3,
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane",
            "min_length": "Hasło jest zbyt krótkie",
        }
    )
    new_password2 = forms.CharField(
        label="Powtórz hasło",
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane",
        }
    )

    def clean_old_password(self):
        # TODO Add implementation checking the current password.
        return self.cleaned_data.get('old_password')

    def clean_new_password2(self):
        password = self.cleaned_data.get('new_password')
        password2 = self.cleaned_data.get('new_password2')
        if password != password2:
            raise forms.ValidationError(
                'Hasła są różne',
                code='pass_not_match'
            )
        return password


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(
        label="Nowy adres",
        error_messages={
            "required": "To pole jest wymagane",
            "invalid": "Podany adres jest nieprawidłowy",
        },
        # FIXME widget size should not be specified here
        widget=forms.EmailInput(attrs={"size": "35"})
    )


class ChangePersonalInfoForm(forms.Form):
    first_name = forms.CharField(
        label="Imię",
        required=False
    )
    last_name = forms.CharField(
        label="Nazwisko",
        required=False
    )


# Exam administration and creation forms

class UploadExamFileForm(forms.Form):
    """
    Form where the file with exam data can be uploaded.
    Currently accepts css files only.
    """
    error_css_class = 'error'
    required_css_class = 'required'

    exam_name = forms.CharField(max_length=32)
    num_questions = forms.IntegerField(label='Number of questions')
    file = forms.FileField(label='csv file')
    has_headers = forms.BooleanField(
        required=False,
        help_text='The file has headers row'
    )
    # TODO Parse file in the cleaning section.
    # TODO Add file validation (eg. json-schema) here.


class ExamCodeForm(forms.Form):
    code = forms.CharField(
        label='Kod',
        error_messages={
            'required': 'Pole jest wymagane'
        },
        widget=forms.TextInput(attrs={'maxlength': 16})
    )

    def __init__(self, *args, exam, **kwargs):
        """
        Initializes a form accepting exam code.
        Binds the exam to the form, so that the code validation will check
        if the code matches the exam.
        :param args: arguments passed to the django.forms.Form
        :param exam: id exam bound to the entered code
        :param kwargs: kwargs passed to the django.forms.form
        """
        super().__init__(*args, **kwargs)
        self._exam_id = exam.id

    def clean_code(self):
        """
        Checks if the code for the previously bound exam id is present in the
        database. Raises form validation error if not.
        :return: cleaned code
        """
        code = self.cleaned_data.get('code')
        if self._exam_id is None:
            raise RuntimeError('Exam not bound')
        valid = (ExamCode.objects.filter(code=code)
                                 .filter(exam_id=self._exam_id)
                                 .exists())
        if not valid:
            raise forms.ValidationError(
                'Nieprawidłowy kod',
                code='incorrect_code'
            )
        return code


# Answering questions

class QuestionForm(forms.Form):
    def __init__(self, *args, question_type, answer_choices, **kwargs):
        """
        Initializes a dynamic question form with specified answers.
        :param args: Arguments passed to the django.forms.Form
        :param question_type: one of the questions types
        :param answer_choices: list of answers choice tuples consisting of
            answer id and answer text
        :param kwargs: keyword arguments passed to the django.forms.Form
        :type question_type: str
        :type answer_choices: list[tuple[int, str]]
        """
        super().__init__(*args, **kwargs)
        self._question_type = question_type
        if question_type == Question.SINGLE_CHOICE:
            form_field_cls = forms.ChoiceField
            widget = forms.RadioSelect()
        elif question_type == Question.MULTIPLE_CHOICE:
            form_field_cls = forms.MultipleChoiceField
            widget = forms.CheckboxSelectMultiple()
        else:
            raise AssertionError("Invalid question type '%s'" % question_type)
        self.fields['answer'] = form_field_cls(
            label="Odpowiedź",
            choices=answer_choices,
            widget=widget,
            error_messages={
                "required": "Wybierz co najmniej jedną odpowiedź.",
                "invalid_choice": "%(value)s nie jest jedną z "
                                  "dostępnych opcji."
            }
        )

    def clean_answer(self):
        ans = self.cleaned_data.get('answer')
        if self._question_type == Question.SINGLE_CHOICE:
            return int(ans)
        elif self._question_type == Question.MULTIPLE_CHOICE:
            return [int(a) for a in ans]
        else:
            raise AssertionError('Invalid question type')
