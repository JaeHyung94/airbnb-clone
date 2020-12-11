from django import forms
from django.contrib.auth.models import User
from . import models


class LoginForm(forms.Form):

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        try:
            user = models.User.objects.get(email=email)

            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error("password", forms.ValidationError("Password is Wrong"))
        except models.User.DoesNotExist:
            self.add_error("email", forms.ValidationError("User Does Not Exist"))


""" Signup with normal Form"""
# class SignupForm(forms.Form):

#     first_name = forms.CharField(max_length=80)
#     last_name = forms.CharField(max_length=80)
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput, label="Password")
#     password1 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

#     def clean_email(self):
#         email = self.cleaned_data.get("email")

#         try:
#             models.User.objects.get(email=email)
#             raise forms.ValidationError("User already exists with this email")
#         except models.User.DoesNotExist:
#             return email

#     def clean_password1(self):
#         password = self.cleaned_data.get("password")
#         password1 = self.cleaned_data.get("password1")

#         if password == password1:
#             return password
#         else:
#             raise forms.ValidationError("Password confirmation does not match")

#     def save(self):
#         first_name = self.cleaned_data.get("first_name")
#         last_name = self.cleaned_data.get("last_name")
#         email = self.cleaned_data.get("email")
#         password = self.cleaned_data.get("password")

#         user = models.User.objects.create_user(email, email=email, password=password)
#         user.first_name = first_name
#         user.last_name = last_name

#         user.save()

""" Signup with Model Form"""


class SignupForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = ("first_name", "last_name", "email")

    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    def clean_password1(self):
        password = self.cleaned_data.get("password")
        password1 = self.cleaned_data.get("password1")

        if password == password1:
            return password
        else:
            raise forms.ValidationError("Password confirmation does not match")

    def save(self, *args, **kwargs):
        user = super().save(commit=False)
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user.username = email
        user.set_password(password)

        user.save()