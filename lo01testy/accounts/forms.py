import re

from django import forms
from django.utils.html import escape
from django.contrib.auth.models import User

from .models import RegistrationCode


class LoginForm(forms.Form):
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
        max_length=50,
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane",
            "max_length": "Maksymalna ilość znaków: 50",
        }
    )


class RegistrationForm(forms.Form):
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
        max_length=50,
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane",
            "min_length": "Hasło jest zbyt krótkie",
            "max_length": "Hasło nie moze zawierać więcej niż 30 znaków"
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
        username = self.cleaned_data.get('username')
        if re.search(r'[^\w@\.\-+]', username):
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
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError(
                'Hasła są różne',
                code='pass_not_match'
            )
        return password

    def clean_code(self):
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
    old_password = forms.CharField(
        label="Stare hasło",
        max_length=50,
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane",
            "max_length": "Maksymalna ilość znaków: 50",
        }
    )

    new_password = forms.CharField(
        label="Nowe hasło",
        min_length=3,
        max_length=50,
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane",
            "min_length": "Hasło jest zbyt krótkie",
            "max_length": "Maksymalna ilość znaków: 50",
        }
    )

    new_password2 = forms.CharField(
        label="Powtórz hasło",
        max_length=50,
        widget=forms.PasswordInput,
        error_messages={
            "required": "To pole jest wymagane",
            "max_length": "Maksymalna ilość znaków: 50",
        }
    )

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
        widget=forms.EmailInput(attrs={"size": "35"})
    )


class ChangePersonalForm(forms.Form):
    first_name = forms.CharField(
        label="Imię",
        required=False
    )
    last_name = forms.CharField(
        label="Nazwisko",
        required=False
    )
