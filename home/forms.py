from django import forms
from django.forms import TextInput, EmailInput
from .models import *
from django.forms import ModelForm, DateInput
from datetime import timedelta
from django.core.validators import RegexValidator, validate_email
import re
from django.utils.timezone import now
from .models import Event
from django.db.models import Q
from django.utils import timezone

class FutureDateInput(forms.DateInput):
    input_type = 'datetime-local'
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
     validators=[RegexValidator(r'^[a-zA-Z ]+$', 'Enter a valid name.')],
    required=True
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'type':'text','placeholder': 'UserName', 'class': 'form-control', 'autocomplete': 'off'}),
        validators=[RegexValidator(r'^[^0-9][a-zA-Z0-9+]+$', 'Enter a valid username.')],
        required=True

    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'type':'email','placeholder': 'Email', 'class': 'form-control', 'autocomplete': 'off'}),
        validators=[validate_email],
        required=True
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'tel', 'placeholder': 'Phone', 'class': 'form-control', 'autocomplete': 'off', 'minlength': '10', 'maxlength': '10'}),
        validators=[RegexValidator(r'^[1-9]\d{9}$', 'Enter a valid phone number')],
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'type':'password','placeholder': 'Password', 'class': 'form-control', 'autocomplete': 'off'}),
        validators=[RegexValidator(r'^(?=.*\d)(?=.*[a-zA-Z]).{8,}$', 'Password must contain at least 8 characters with at least one digit and one letter.')],
        required=True
    )
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            self._errors['username'] = self.error_class(["This username is already in use. Please choose a different one."])
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        arr=email.split("@")
        print(arr)
        regex = re.compile('[_!#$%^&*()<>?/\|}{~:]')
        if regex.search(arr[0]) is None and regex.search(arr[1]) is None:
            print("String is accepted")
        else:
            self._errors['email'] = self.error_class(["This email cannot contain special characters except @ and ."])
        if User.objects.filter(email=email).exists():
            self._errors['email'] = self.error_class(["This email address is already in use. Please use a different one."])
        return email
    
    def clean_phone(self):
       phone=self.cleaned_data.get("phone")
       if User.objects.filter(phone=phone).exists():
          self._errors['phone'] = self.error_class(["This Phone is already in use"])
       return phone
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and name.startswith(' '):
            name = name.lstrip()
        return name
          

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
      six_months_from_now = now() + timedelta(days=180)
      self.fields['start_time'].widget.attrs['max'] = six_months_from_now.strftime('%Y-%m-%dT%H:%M')
      self.fields['end_time'].widget.attrs['max'] = six_months_from_now.strftime('%Y-%m-%dT%H:%M')
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
       self.fields['title'].disabled = True
       self.fields['start_time'].disabled = True
       self.fields['end_time'].disabled = True
       self.fields['description'].disabled = True
       self.fields['event_cost'].disabled=True
  def clean_event_cost(self):
    cost = self.cleaned_data.get("event_cost")
    if cost is not None and (cost < 0 or not isinstance(cost, int)):
       self._errors['event_cost'] = self.error_class(["Invalid cost. Please provide a valid integer."])
    return cost
  def clean_title(self):
    title = self.cleaned_data.get("title")
    special_chars_regex = re.compile('[_!#$%^&*()<>?/\|}{~:]')
    digit_regex = re.compile(r'\d')
    if special_chars_regex.search(title):
        raise forms.ValidationError("Title cannot contain special characters.")
    elif digit_regex.search(title):
        raise forms.ValidationError("Title cannot contain numbers.")
    else:
       return title
    
  def clean_description(self):
    description=self.cleaned_data.get("description")
    regex = re.compile('[_!#$%^&*()<>?/\|}{~:]')
    if regex.search(description) is None:
       print("String is accepted")
    else:
       self._errors['description'] = self.error_class(["Invalid Input"])
    return description
  
  def clean(self):
      cleaned_data = super().clean()
      start_time =  cleaned_data.get("start_time")
      print("-------------------------------------------------------------------")
      print(cleaned_data)
      created_by=cleaned_data.get("created_by")
      print(start_time)
      end_time = cleaned_data.get("end_time")
      print(end_time)
      if start_time.date()==end_time.date():
         print(end_time-start_time)
         time_difference=end_time-start_time
         hours_difference = time_difference.total_seconds() / 3600
         print(hours_difference)
         if hours_difference >= 1:
            print("Session is valid. Duration:", hours_difference, "hours")
         else:
            print("Session is less than 1 hour. Ignoring.")
            self._errors['end_time'] = self.error_class(["Minimum One hour Session."])
            self._errors['start_time'] = self.error_class(["Minimum One hour Session."])
      if start_time>end_time:
          print(f"In clean{start_time.date()}{end_time.date()}")
          self._errors['end_time'] = self.error_class(["End date cannot be more than start date."])
          self._errors['start_time'] = self.error_class(["End date cannot be more than start date."])
      start_time_obj = start_time.strftime('%H:%M:%S')
      start_date_obj = start_time.strftime('%Y-%m-%d')
      end_date_obj = end_time.strftime('%Y-%m-%d')
      end_time_obj = end_time.strftime('%H:%M:%S')
      current_datetime = datetime.now()
      if start_time.date() == current_datetime.date() and start_time.time() < current_datetime.time():
          self._errors['start_time'] = self.error_class([f"select time more than {current_datetime.time().strftime('%H:%M')}"])
      if end_time.date() == current_datetime.date() and end_time.time() < current_datetime.time():
         self._errors['end_time'] = self.error_class([f"select time more than {current_datetime.time().strftime('%H:%M')}"])
      if Event.objects.filter(Q(created_by=created_by) & Q(start_time__date__gt=start_date_obj,end_time__date__lt=end_date_obj)).exists():
         print(Event.objects.filter(Q(created_by=created_by) & Q(start_time__date__gt=start_date_obj,end_time__date__lt=end_date_obj)).exists())
         self._errors['end_time'] = self.error_class(["Already an event exist within this timeline."])
         self._errors['start_time'] = self.error_class(["Already an event exist within this timeline"])
      if Event.objects.filter(Q(created_by=created_by) & Q(start_time__date__gte=start_date_obj,end_time__date__lte=end_date_obj) &
                                  (Q(start_time__time__lte=start_time_obj,end_time__time__gte=end_time_obj)|
                                  Q(start_time__time__gte=start_time_obj,end_time__time__lte=end_time_obj)|
                                  Q(start_time__time__lte=end_time_obj,end_time__time__gte=end_time_obj)|
                                  Q(start_time__time__lte=start_time_obj,end_time__time__gte=start_time_obj))).exists():
         print(Event.objects.filter(Q(created_by=created_by) & Q(start_time__date__gte=start_date_obj,end_time__date__lte=end_date_obj) &
                                  (Q(start_time__time__lte=start_time_obj,end_time__time__gte=end_time_obj)|
                                  Q(start_time__time__gte=start_time_obj,end_time__time__lte=end_time_obj)|
                                  Q(start_time__time__lte=end_time_obj,end_time__time__gte=end_time_obj)|
                                  Q(start_time__time__lte=start_time_obj,end_time__time__gte=start_time_obj))))
         self._errors['end_time'] = self.error_class(["Already an event exist on same date."])
         self._errors['start_time'] = self.error_class(["Already an event exist on same date."])
      # time_difference = end_time - start_time
      # if time_difference < timedelta(hours=1):
      #    self._errors['end_time'] = self.error_class(["Minimum One hour Session."])
      #    self._errors['start_time'] = self.error_class(["Minimum One hour Session."])
      return cleaned_data
    

 


class SessionRequestForm(forms.ModelForm):
    class Meta:
        model = SessionRequest
        exclude=['student','teacher','is_approved']
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
               field.widget.attrs['class'] = 'form-control'
            six_months_from_now = now() + timedelta(days=180)
            self.fields['start_time'].widget.attrs['max'] = six_months_from_now.strftime('%Y-%m-%dT%H:%M')
            self.fields['end_time'].widget.attrs['max'] = six_months_from_now.strftime('%Y-%m-%dT%H:%M')
            self.fields['title']=forms.ChoiceField(choices=instance.title_choices)
            self.fields['title'].widget.attrs['class'] = 'form-control'
            self.fields['title'].choices = instance.title_choices

 
            
    
class ResetSessionModelForm(forms.ModelForm):
    class Meta:
        model = SessionRequest
        exclude=['student','teacher','is_approved','start_time','end_time']
    def __init__(self, *args, **kwargs):
        super(ResetSessionModelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
           field.widget.attrs['class'] = 'form-control'