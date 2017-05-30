from django.shortcuts import redirect


def index(request):
    """The index page which redirects to login page or user profile.

    name: index
    URL: /
    """
    if request.user.is_authenticated():
        return redirect('accounts:profile')
    else:
        return redirect('accounts:login')
