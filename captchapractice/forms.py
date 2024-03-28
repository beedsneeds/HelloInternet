# from django.forms import ModelForm
# from django import forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


from .models import CaptchaImage, ImageSlice

class CaptchaImageForm(forms.ModelForm):
    class Meta:
        model = CaptchaImage


class ImageSliceForm(forms.ModelForm):
    class Meta:
        model = ImageSlice
        fields = ["element_presence"]


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


