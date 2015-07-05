from django import forms


class LoginForm(forms.Form):
	username = forms.CharField(
        label="Użytkownik",
        max_length=25,
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
