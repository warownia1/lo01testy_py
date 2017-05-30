import django.http
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from app.forms import LoginForm, RegistrationForm
from app.models import UserX, RegistrationCode


def login_view(request, username=None):
    """
    Displays login form and runs authentication process.
    If username is given, then the login field is auto-filled.

    name: accounts:login
    URL: /accounts/login/
         /accounts/login/<username>/
    """
    next_page = request.GET.get('next')
    form = LoginForm(request.POST or None, initial={'username': username})
    if form.is_valid():
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if (user is not None) and user.is_active:
            login(request, user)
            return redirect(next_page or 'accounts:profile')
        else:
            error = ValidationError(
                'Nieprawidłowy login lub hasło',
                code='incorrect_credentials'
            )
            form.add_error('username', error)
    return render(
        request, 'accounts/login.html',
        {'form': form, 'next': next}
    )


def logout_view(request):
    """
    Finishes the session and logs the user out

    name: accounts:logout
    url: /accounts/logout/
    """
    request.session.flush()
    logout(request)
    return redirect('accounts:login')


def register_view(request):
    """
    Displays a registration form and runs user registration.

    name: accounts:registration
    URL: /accounts/register
    """
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data['username']
        user = User.objects.create_user(
            username,
            password=form.cleaned_data['password']
        )
        code = form.cleaned_data['code']
        UserX.objects.create(user=user, code=code)
        RegistrationCode.objects.filter(code=code).delete()
        return redirect('accounts:login', username)
    return render(
        request, 'accounts/registration.html',
        {'form': form}
    )


@login_required
def profile_view(request):
    """
    Shows a profile information.
    name: accounts:user_profile
    URL: /accounts/profile/
    """
    return render(
        request, 'accounts/user_profile.html',
        {'view_user': request.user}
    )


@login_required
def settings_view(request):
    """
    Displays an account settings menu.

    name: accounts:account_settings
    URL: /accounts/settings/
    """
    raise django.http.Http404("Not implemented yet")
    return render(request, 'account_settings.html')
