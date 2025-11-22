from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Gig, ProjectPost

User = get_user_model()

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class GigForm(forms.ModelForm):
    class Meta:
        model = Gig
        fields = ['title', 'description', 'category', 'price','image']


class ProjectPostForm(forms.ModelForm):
    class Meta:
        model = ProjectPost
        fields = ['title', 'description', 'budget']

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username','email','password1','password2']        