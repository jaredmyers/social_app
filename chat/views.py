from django.shortcuts import render
from django.urls import reverse
from .forms import LoginForm, RegisterForm
from .user_processing import process_login

def login(request):
    '''main login page'''

    # validate post info and send to db for validation
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            print("loginform valid.")
            username = form.cleaned_data['username']
            pw = form.cleaned_data['pw']

            authentication = process_login(username, pw)
            if not authentication:
                print("login fail")
                bad_login = True
                return render(request, "login.html", {
                    "form": form, "bad_login": bad_login
                    })
            else:
                print("authentication successful")
                return render(request, "index.html")
        else:
            print("form not valid")
            bad_login = True
            return render(request, "login.html", {
                "form": form, "bad_login": bad_login
                })

    # return render(request, 'index.html')
    return render(request, 'login.html', {
        "form": LoginForm(),
        })


def c_home(request):
    print("c_home is functional")


def index(request):
    return render(request, 'index.html')


def register(request):
    '''Register a new user'''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("Register Form Valid")
            username = form.cleaned_data['username']
            pw = form.cleaned_data['pw']
            pw2 = form.cleaned_data['pw2']

            print("username = " + username)
            print("pw  = " + pw)
            print("pw2 = " + pw2)

    return render(request, 'register.html', {
        "form": RegisterForm()
        })
