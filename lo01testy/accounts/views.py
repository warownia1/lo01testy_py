from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.forms import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import LoginForm, RegisterForm
from .models import Student, RegisterCode


def index(request):
    """The index page which redirects to login page or user profile.

    name: index
    URL: /
    """
    if request.user.is_authenticated():
        return redirect('accounts:user_profile')
    else:
        return redirect('accounts:login')


def login_user(request, username=None):
    """Displays login form and runs authentication process.

    If username is given, then the login field is auto-filled.

    name: accounts:login
    URL: /accounts/login/
         /accounts/login/<username>/
    """
    next = request.GET.get("next")
    if username:
        form = LoginForm(initial={'username': username})
        return render(request, 'login.html',
            {"form": form, "next": next}
        )
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=request.POST['username'],
                password=request.POST['password']
            )
            if (user is not None) and (user.is_active):
                login(request, user)
                target_page = request.GET.get('next', 'accounts:user_profile')
                return redirect(target_page)
            else:
                error = ValidationError(
                    "Nieprawidłowy login lub hasło",
                    code='incorrect_credentials'
                )
                form.add_error('username', error)
    else:
        form = LoginForm()
    return render(request, 'login.html',
        {"form": form, "next": next}
    )


def logout_user(request):
    """Finishes the session and logs the user out.

    name: accounts:logout
    URL: /accounts/logout/
    """
    request.session.flush()
    logout(request)
    return redirect('accounts:login')


def register_user(request):
    """Displays registration form and runs user registration.

    name: accounts:registration
    URL: /acounts/register/
    """
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
            # redirect user to login page with username already filled in
            return redirect('accounts:login', username)
    else:
        form = RegisterForm()
    return render(request, 'registration.html', {"form": form})


@login_required
def user_profile(request, id=None, username=None):
    """Shows the basic user profile info.

    Arguments:
      id (int): id of the user to display
      username (string): username of the user to display
    only one or neither argument should be passed to the function
    if no argument given, displays the currently signed user info.

    name: accounts:user_profile
    URL: /accounts/user/id/<id>/
         /accounts/user/
         /accounts/user/<username>/

    """
    if id is not None:
        user = get_object_or_404(User, id=id)
    elif username is not None:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    return render(request, 'user_profile.html', {"user": user})
