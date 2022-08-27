from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
import re

class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"

class DateInput(forms.DateInput):
    input_type = "date"

def defaultStart():
    return (datetime.now()+ timedelta(hours=1)).strftime("%Y-%m-%dT%H:00:00")

def defaultEnd():
    return (datetime.now()+ timedelta(hours=2)).strftime("%Y-%m-%dT%H:00:00")

class StartDateTimeLocalField(forms.DateTimeField):
    # Set DATETIME_INPUT_FORMATS here because, if USE_L10N
    # is True, the locale-dictated format will be applied
    # instead of settings.DATETIME_INPUT_FORMATS.
    # See also:
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Date_and_time_formats

    input_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M"
    ]
    widget = DateTimeLocalInput(format="%Y-%m-%dT%H:%M", attrs={'value': defaultStart()})

class EndDateTimeLocalField(forms.DateTimeField):
    # Set DATETIME_INPUT_FORMATS here because, if USE_L10N
    # is True, the locale-dictated format will be applied
    # instead of settings.DATETIME_INPUT_FORMATS.
    # See also:
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Date_and_time_formats

    input_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M"
    ]
    widget = DateTimeLocalInput(format="%Y-%m-%dT%H:%M", attrs={'value': defaultEnd()})

class UntilDateField(forms.DateField):
    widget = DateInput(format="%Y-%m-%d")


class NewEventForm(forms.Form):
    TIME_ZONES =(
        ("America/Los_Angeles", "Pacific Time"),
        ("America/Denver", "Mountain Time"),
        ("America/Chicago", "Central Time"),
        ("America/New_York", "Eastern Time"),
    )

    REPEAT_OPTIONS =(
        ("NONE", "none"),
        ("DAILY", "daily"),
        ("WEEKLY", "weekly"),
    )

    title = forms.CharField(max_length=255, label="Title", required=False)
    start = StartDateTimeLocalField(label="Start time")
    end = EndDateTimeLocalField(label="End time")
    tz = forms.ChoiceField(choices = TIME_ZONES, label="Time zone")
    freq = forms.ChoiceField(choices = REPEAT_OPTIONS, label="Repeat")
    count = forms.IntegerField(required=False)
    until = UntilDateField(required=False)
    guests = forms.CharField(widget=forms.Textarea, label="Guests", required=False)
    location = forms.CharField(max_length=255, label="Location", required=False)
    desc = forms.CharField(widget=forms.Textarea, label="Description", required=False)

    def clean(self):
        errors=[]

        def iso(date):
            return date.strftime("%Y-%m-%dT%H:%M:00")

        cleaned_data = super().clean()

        try:
            start = iso(cleaned_data.get("start"))
        except:
            start = None
            self._errors["start"] = self.error_class(["Invalid date."])

        try:
            end = iso(cleaned_data.get("end"))
        except:
            end = None
            self._errors["end"] = self.error_class(["Invalid date."])

        # Check that start datetime is before end datetime.
        if start and end and start > end:
            errors.append(ValidationError(_('Invalid dates: start time must be before end time.'), code='invalid_dates'))

        #Recurrence
        recurrence = ''
        if cleaned_data.get("freq") != "NONE":
            recurrence = 'RRULE:FREQ=' + cleaned_data.get("freq") + ';'
            if cleaned_data.get("count") and cleaned_data.get("until"):
                errors.append(ValidationError(_('Invalid recurrence: Please choose either "count" or "until", not both.'), code='both_count_and_until'))
            elif cleaned_data.get("count"):
                recurrence += 'COUNT=' + str(cleaned_data.get("count"))
            elif cleaned_data.get("until"):
                recurrence += 'UNTIL=' + (cleaned_data.get("until")+ timedelta(days=2)).strftime("%Y%m%d")
                #adding 2 days because of what appears to be a glitch in Google Calendar or the API
                print(recurrence)
            else:
                errors.append(ValidationError(_('Invalid recurrence: Please choose either "count" or "until" to set the number of repeats.'), code='missing_count_and_until'))

        #Guests
        text = cleaned_data.get("guests")
        emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", text) #extract emails from text using regex
        print(emails)
        guests = []
        for email in emails:
            guests.append({'email': email})

        if errors:
            raise ValidationError(errors)

        event = {
            'summary': cleaned_data.get("title"),
            'location': cleaned_data.get("location"),
            'description': cleaned_data.get("desc"),
            'start': {
                'dateTime': start,
                'timeZone': cleaned_data.get("tz"),
            },
            'end': {
                'dateTime': end,
                'timeZone': cleaned_data.get("tz"),
            },
            'attendees': guests,
            'reminders': {
                'useDefault': False,
                'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        if recurrence:
            event['recurrence'] = [recurrence]

        return event
