from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import ValidationError
from django.contrib.auth import authenticate, login

from .forms import LoginForm, RegisterForm



def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=request.POST['username'],
                password=request.POST['password']
            )
            if (user is not None) and (user.is_active):
                login(request, user)
                return redirect('/accounts/browse/')
            else:
                error = ValidationError(
                    "Nieprawidłowy login lub hasło",
                    code='incorrect_login'
                )
                form.add_error('username', error)
    else:
        form = LoginForm()
    return render(request, 'registration/login_form.html', {"form": form})

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            return HttpResponse("valid registration form")
    else:
        form = RegisterForm()
    return render(request, 'registration/register_form.html', {"form": form})
        
    