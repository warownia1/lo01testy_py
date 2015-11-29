from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.forms import ValidationError
from django.contrib.auth import authenticate, login, logout, \
                                update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
                   ChangeEmailForm, ChangePersonalForm
from .models import Student, RegistrationCode


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
        return render(
            request, 'login.html',
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
    return render(
        request, 'login.html',
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
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            code = form.cleaned_data['code']
            # Create new entry in User and Student.
            new_user = User.objects.create_user(username, password=password)
            Student(user=new_user, code=code)
            new_user.student.save()
            # Delete code used for registration.
            RegistrationCode.objects.get(code=code).delete()
            # redirect user to login page with username already filled in
            return redirect('accounts:login', username)
    else:
        form = RegistrationForm()
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


@login_required
def account_settings(request):
    """Displays the account settings menu

    name: accounts:account_settings
    URL: /accounts/settings/
    """
    return render(request, 'account_settings.html', {"user": request.user})


@login_required
def change_email(request):
    """Change the user's email address

    name: accounts: change_email
    URL: /accounts/settings/email/
    """
    if request.method == "POST":
        form = ChangeEmailForm(request.POST)
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()
    else:
        form = ChangeEmailForm(
            initial={"email": request.user.email}
        )
    return render(request, 'change_email.html', {"form": form})


@login_required
def change_password(request):
    """Change the user's password

    name: accounts:change_password
    URL: /accounts/settings/password/
    """
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            if request.user.check_password(old_password):
                new_password = form.cleaned_data['new_password']
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                return redirect('accounts:change_password')
            else:
                error = ValidationError(
                    "Podane hasło jest nieprawidłowe",
                    code="incorrect_password"
                )
                form.add_error('old_password', error)
    else:
        form = ChangePasswordForm()
    return render(request, 'change_password.html', {"form": form})


@login_required
def change_personal(request):
    """Change the personal data of the user.

    name: accounts:change_personal
    URL: /accounts/settings/personal/
    """
    if request.method == "POST":
        form = ChangePersonalForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.save()
    else:
        form = ChangePersonalForm(
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name
            }
        )
    return render(request, 'change_personal.html', {"form": form})
