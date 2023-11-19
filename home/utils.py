from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import *
import random

class Calendar(HTMLCalendar):
	def __init__(self, year=None, month=None):
		self.year = year
		self.month = month
		super(Calendar, self).__init__()
	# formats a day as a td
	# filter events by day
	def formatday(self, day, events,user,user_type):
		# events_per_day = events.filter(start_time__day=day)
		if user_type == "teacher":
			teacher = Teacher.objects.get(user=user)
			events_per_day = events.filter(start_time__day=day, created_by=teacher, booked_by=None)
		elif user_type == "student":
			student = Student.objects.get(user=user)
			events_per_day = events.filter(start_time__day=day, booked_by=None, created_by__in=student.teachers.all())
		print(user_type)
		color_list = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#ff8000", "#0080ff", "#80ff00", "#8000ff", "#ff0080"]
		try:
			li = [event.get_available_url(user_type) for event in events_per_day if event.booked_by is None]
		except Exception as e:
			print(f"Not Working: {e}")
		d = ''.join(f'<li style="background-color: {random.choice(color_list)}; padding: 4px; margin: 4px; text-align: center; width: {len(event[1]) * 20}px;">{event[0]} <span style="font-weight: bold; font-style: italic;">[{event[2]}]</span></li>' for event in li)
		# d = ''.join(f'<li>{event.get_html_url}</li>' for event in events_per_day)
		if day != 0:
			return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
		return '<td></td>'

	# formats a week as a tr
	def formatweek(self, theweek, events,user,user_type):
		week = ''.join(self.formatday(d, events ,user,user_type) for d, weekday in theweek)
		return f'<tr> {week} </tr>'

	# formats a month as a table
	# filter events by year and month
	def formatmonth(self, user,user_type,withyear=True):
		events = Event.objects.filter(start_time__year=self.year, start_time__month=self.month)
		# print("User-type is",user_type)
		cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
		cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
		cal += f'{self.formatweekheader()}\n'
		for week in self.monthdays2calendar(self.year, self.month):
			cal += f'{self.formatweek(week, events ,user,user_type)}\n'
		return cal
	