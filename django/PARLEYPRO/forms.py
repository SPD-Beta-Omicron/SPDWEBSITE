# forms.py
from django import forms
from .models import Vote_Poll

class VotePollForm(forms.ModelForm):
    class Meta:
        model = Vote_Poll
        fields = ['Vote_Poll_Name']
        labels = {
            'Vote_Poll_Name': 'Poll Name'
        }
        widgets = {
            'Vote_Poll_Name': forms.TextInput(attrs={'class': 'form-control'})
        }