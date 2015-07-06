from django import forms
from django.utils.html import escape
from django.contrib.auth.models import User

from accounts.models import RegisterCode


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
            "max_length": "maksymalna ilość znamów: 50",
        }
    )

    
class RegisterForm(forms.Form):
    username = forms.CharField(
        label="Nazwa użytkownika",
        min_length=3,
        max_length=30,
        error_messages={
            "required": "To pole jest wymagane",
            "min_length": "Login jest zbyt krótki",
            "max_width": "Login nie może zawierać więcej niż 30 znaków"
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
        username = escape(username)
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
        return password2
        
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not RegisterCode.objects.filter(code=code).exists():
            raise forms.ValidationError(
                "Niewłaściwy kod",
                code='invalid_code'
            )
        return code
    