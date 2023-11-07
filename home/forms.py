from django import forms
from django.forms import TextInput, EmailInput
from .models import *
USER_CHOICES= [
    ('teacher', 'Teacher'),
    ('student', 'Student'),
    ]
class UserRegistration(forms.Form):
   name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name', 'style': 'width: 300px;', 'class': 'form-control'}))
   email=forms.EmailField(widget=forms.EmailInput(attrs={'placeholder' :'Email', 'style': 'width: 300px;', 'class': 'form-control'}))
   password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' :'Password', 'style': 'width: 300px;', 'class': 'form-control'}))

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
   