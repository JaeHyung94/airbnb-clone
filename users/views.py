import os
import requests
from django.views import View
from django.views.generic import FormView, DetailView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from . import forms, models

# Create your views here.

"""Handmade login View"""
# class LoginView(View):
#     def get(self, request):
#         form = forms.LoginForm

#         return render(request, "users/login.html", {"form": form})

#     def post(self, request):
#         form = forms.LoginForm(request.POST)

#         if form.is_valid():
#             email = form.cleaned_data.get("email")
#             password = form.cleaned_data.get("password")

#             user = authenticate(request, username=email, password=password)

#             if user is not None:
#                 login(request, user)
#                 return redirect(reverse("core:home"))

#         return render(request, "users/login.html", {"form": form})

"""Using Django Built-in LoginView"""


class LoginView(FormView):
    template_name = "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        user = authenticate(self.request, username=email, password=password)

        if user is not None:
            login(self.request, user)

        return super().form_valid(form)


def log_out(request):
    logout(request)
    return redirect(reverse("core:home"))


""" Custom Signup Form """
# class SignupView(FormView):
#     template_name = "users/signup.html"
#     form_class = forms.SignupForm
#     success_url = reverse_lazy("core:home")

#     def form_valid(self, form):
#         form.save()

#         email = form.cleaned_data.get("email")
#         password = form.cleaned_data.get("password")

#         user = authenticate(self.request, username=email, password=password)

#         if user is not None:
#             login(self.request, user)

#         user.verify_email()

#         return super().form_valid(form)

""" User Creation Form """


class SignupView(FormView):
    template_name = "users/signup.html"
    form_class = forms.SignupForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        form.save()

        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        user = authenticate(self.request, username=email, password=password)

        if user is not None:
            login(self.request, user)

        user.verify_email()

        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # To do: add success message
    except models.User.DoesNotExist:
        # To do: add error message
        pass
    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get("GH_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
    )


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")
        code = request.GET.get("code", None)

        if code is not None:
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )

            token_json = token_request.json()
            error = token_json.get("error", None)

            if error is not None:
                raise GithubException("Can't get access token")
            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )

                profile_json = profile_request.json()
                username = profile_json.get("login", None)

                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    bio = profile_json.get("bio")

                    bio = "" if bio is None else bio

                    try:
                        user = models.User.objects.get(email=email)

                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(
                                f"Please log in with: {user.login_method}"
                            )
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,
                            first_name=name,
                            username=email,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(request, f"Welcome back {user.first_name}")
                    return redirect(reverse("core:home"))

                else:
                    raise GithubException("Can't get your profile")

        else:
            raise GithubException("Can't get code")
    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


def kakao_login(request):
    API_KEY = os.environ.get("KAKAO_SECRET")
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"

    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={API_KEY}&redirect_uri={redirect_uri}&response_type=code"
    )


class KakaoExeption(Exception):
    pass


def kakao_callback(request):
    try:
        client_id = os.environ.get("KAKAO_SECRET")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        code = request.GET.get("code")

        if code is not None:
            token_request = requests.post(
                f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
            )

            token_json = token_request.json()
            access_token = token_json.get("access_token")
            error = token_json.get("error", None)

            if error is not None:
                raise KakaoExeption("Can't get authorization code")
            else:
                profile_request = requests.get(
                    "https://kapi.kakao.com/v2/user/me",
                    headers={"authorization": f"Bearer {access_token}"},
                )

                profile_json = profile_request.json()
                user_id = profile_json.get("id")

                if user_id is None:
                    raise KakaoExeption("Please also give me your email")

                name = profile_json.get("kakao_account").get("profile").get("nickname")
                email = profile_json.get("kakao_account").get("email")

                try:
                    user = models.User.objects.get(email=email)

                    if user.login_method != models.User.LOGIN_KAKAO:
                        raise KakaoExeption(f"Please log in with: {user.login_method}")
                except models.User.DoesNotExist:
                    user = models.User.objects.create(
                        email=email,
                        username=email,
                        first_name=name,
                        login_method=models.User.LOGIN_KAKAO,
                        email_verified=True,
                    )
                    user.set_unusable_password()
                    user.save()
                login(request, user)
                messages.success(request, f"Welcome back {user.first_name}")
                return redirect(reverse("core:home"))
        else:
            raise KakaoExeption()

    except KakaoExeption as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):

    model = models.User
    context_object_name = "user_obj"


class UpdateProfileView(UpdateView):

    models = models.User
    template_name = "users/update-profile.html"
    fields = (
        "email",
        "first_name",
        "last_name",
        "avatar",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency",
    )

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        self.object.username = email
        self.object.save()
        return super().form_valid(form)


class UpdatePasswordView(PasswordChangeView):
    template_name = "users/update-password.html"