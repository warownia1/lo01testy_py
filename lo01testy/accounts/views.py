from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.forms import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import LoginForm, RegisterForm
from .models import Student, RegisterCode



def login_user(request, username=None):
    if username:
        form = LoginForm(initial={'username': username})
        return render(request, 'registration/login_form.html', {"form": form})
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=request.POST['username'],
                password=request.POST['password']
            )
            if (user is not None) and (user.is_active):
                login(request, user)
                return redirect('show_user')
            else:
                error = ValidationError(
                    "Nieprawidłowy login lub hasło",
                    code='incorrect_credentials'
                )
                form.add_error('username', error)
    else:
        form = LoginForm()
    return render(request, 'registration/login_form.html', {"form": form})
    
def logout_user(request):
    request.session.flush()
    logout(request)
    return redirect('login')

def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            code = form.cleaned_data['code']
            # Create new entry in User and Student.
            new_user = User.objects.create_user(username, password=password)
            Student(user=new_user)
            new_user.student.save()
            # Delete code used for registration.
            RegisterCode.objects.filter(code=code)[0].delete()
            #redirect user to login page with username already filled in
            return redirect('login', username)
    else:
        form = RegisterForm()
    return render(request, 'registration/register_form.html', {"form": form})

@login_required    
def show_user(request, id=None, username=None):
    if id is not None:
        user = get_object_or_404(User, id=id)
    elif username is not None:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    return render(request, 'main_screen/show_user.html', {"user": user})
