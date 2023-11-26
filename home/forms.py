from django import forms
from django.forms import TextInput, EmailInput
from .models import *
from django.forms import ModelForm, DateInput
from django.utils.timezone import now


class FutureDateInput(forms.DateInput):
    input_type = 'date'
    def get_context(self, name, value, attrs):
        attrs.setdefault('min', now().strftime('%Y-%m-%dT%H:%M'))
        return super().get_context(name, value, attrs)

USER_CHOICES= [
    ('teacher', 'Teacher'),
    ('student', 'Student'),
    ]
class UserRegistration(forms.Form):
   name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Name', 'class': 'form-control', 'autocomplete':'off'}))
   username=forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'UserName', 'class': 'form-control', 'autocomplete':'off'}))
   email=forms.EmailField(widget=forms.EmailInput(attrs={'placeholder' :'Email', 'class': 'form-control','autocomplete':'off'}))
   phone = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Phone', 'class': 'form-control', 'autocomplete': 'off'}))
   password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder' :'Password', 'class': 'form-control','autocomplete':'off'}))

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']

class EventForm(ModelForm):
  class Meta:
    model = Event
    # datetime-local is a HTML5 input type, format to make date time show on fields
    widgets = {
      'start_time': FutureDateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      'end_time': FutureDateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    }
    fields = '__all__'
    # exclude=['created_by','booked_by']

  def __init__(self, request,user,user_type,*args, **kwargs):
     print(user)
     super(EventForm, self).__init__(*args, **kwargs)
     # input_formats parses HTML5 datetime-local input to datetime field
     self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
     self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)
     if user_type == 'teacher':
      self.fields['booked_by'].disabled = True
      self.fields['created_by'].disabled = True
     elif user_type == 'student':
       self.fields['created_by'].disabled = True
       self.fields['booked_by'].disabled = True
       self.fields['title'].disabled = True
       self.fields['start_time'].disabled = True
       self.fields['end_time'].disabled = True
       self.fields['description'].disabled = True
       
     if self.instance and hasattr(self.instance, 'created_by') and self.instance.created_by:
      self.fields['created_by'].disabled = True
      self.fields['booked_by'].initial = user
     if self.instance and hasattr(self.instance, 'booked_by') and self.instance.booked_by:
      self.fields['booked_by'].disabled = True