from django import forms

from .models import ExamCode


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
        if not ExamCode.objects.filter(code=code).filter(exam_id=self.exam_id).exists():
            raise forms.ValidationError(
                "Niewłaściwy kod",
                code='incorrect_code'
            )
        return code
