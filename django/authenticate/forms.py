from django.contrib.auth.forms import UserCreationForm  # User Registration import
from django.contrib.auth.models import User  # User Registration import
from django import forms  # User Registration import


class CreateUserForm(UserCreationForm):

  class Meta(UserCreationForm.Meta):
    model = User
    fields = ['email', 'username', 'password1', 'password2']
