from django import forms
from django.forms import TextInput, EmailInput
from .models import *
from django.forms import ModelForm, DateInput
from django.utils.timezone import now
from django.core.validators import RegexValidator, validate_email

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
    name = forms.CharField(
        widget=forms.TextInput(attrs={'type':'text','placeholder': 'Name', 'class': 'form-control', 'autocomplete': 'off'}),
        validators=[RegexValidator(r'^[a-zA-Z\s]*$', 'Enter a valid username.')]
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'type':'text','placeholder': 'UserName', 'class': 'form-control', 'autocomplete': 'off'}),
        validators=[RegexValidator(r'^[0-9a-zA-Z\s]*$', 'Enter a valid username.')]

    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'type':'email','placeholder': 'Email', 'class': 'form-control', 'autocomplete': 'off'}),
        validators=[validate_email]
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'type':'tel','placeholder': 'Phone', 'class': 'form-control', 'autocomplete': 'off','minlength':'10','maxlength':'10'}),
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'type':'password','placeholder': 'Password', 'class': 'form-control', 'autocomplete': 'off'}),
        validators=[RegexValidator(r'^(?=.*\d)(?=.*[a-zA-Z]).{8,}$', 'Password must contain at least 8 characters with at least one digit and one letter.')]
    )

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


class SessionRequestForm(forms.ModelForm):
    class Meta:
        model = SessionRequest
        exclude=['student','teacher','is_booked']
        widgets = {
      'start_time': FutureDateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      'end_time': FutureDateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      }
        # fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(SessionRequestForm, self).__init__(*args, **kwargs)
        if instance := kwargs.get('instance'):
            print(instance.title_choices)
            for field_name, field in self.fields.items():
               print(field_name)
               print(self.fields.items())
               field.widget.attrs['class'] = 'form-control'
            self.fields['title']=forms.ChoiceField(choices=instance.title_choices)
            self.fields['title'].widget.attrs['class'] = 'form-control'
            self.fields['title'].choices = instance.title_choices
    
    