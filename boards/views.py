from django.shortcuts import render, HttpResponseRedirect
from .models import Calendar
import os
import google_apis_oauth
from googleapiclient.discovery import build
import datetime
from .forms import NewEventForm
from django.urls import reverse, reverse_lazy
from dateutil import parser
from django.contrib import messages

def setup_calendar(request):
    # Load the stored credentials in a variable say 'stringified_token
    stringified_token = request.session.get('key')

    # Load the credentials object using the stringified token.
    creds, refreshed = google_apis_oauth.load_credentials(stringified_token)

    # Using credentials to access Upcoming Events
    service = build('calendar', 'v3', credentials=creds)
    return service

def home(request):
    return render(request, 'home.html')

def calendars(request):
    calendars = Calendar.objects.all()
    return render(request, 'calendars.html', {'calendars': calendars})

def events(request):
    if not request.session.get('key'):
        oauth_url = google_apis_oauth.get_authorization_url(
        JSON_FILEPATH, SCOPES, REDIRECT_URI)
        return HttpResponseRedirect(oauth_url)
    service = setup_calendar(request)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    # Getting upcoming 10 events
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = events_result.get('items', [])

    def format_datetime(value):
        # instead of just date = dateutil.parser.parse(value)
        if isinstance(value, str):
            date = parser.parse(value)
        else:
            date = value
        return date

    days = {}
    for event in events:
        if event['start'].get('date'): # this is if the event is an all-day event
            startDay = event['start'].get('date')
        else:
            start = format_datetime(event['start'].get('dateTime'))
            end = format_datetime(event['end'].get('dateTime'))
            startDay = start.date()
            event['startTime'] = start.time()
            event['endTime'] = end.time()
        if startDay in days.keys():
            days[startDay].append(event)
        else:
            days[startDay] = [event]

    return render(request, 'events.html', {'days': days.items()})

def new_event(request):
    if request.method == 'POST':
        form = NewEventForm(request.POST)
        if form.is_valid():
            event = form.cleaned_data
            service = setup_calendar(request)
            event = service.events().insert(calendarId='primary', body=event).execute()
            messages.success(request, "Your event was created successfully." )
            return HttpResponseRedirect(reverse('events'))
    else:
        form = NewEventForm()

    return render(request,
        'new-event.html', {'form': form})

# The url where the google oauth should redirect
# after a successful login.
REDIRECT_URI = 'https://acsent-calendar.herokuapp.com/google_oauth/callback/'

# Authorization scopes required
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Path of the "client_id.json" file
JSON_FILEPATH = os.path.join(os.getcwd(), 'client_id/client_id_heroku.json')

def RedirectOauthView(request):
    oauth_url = google_apis_oauth.get_authorization_url(
        JSON_FILEPATH, SCOPES, request.build_absolute_uri(REDIRECT_URI))
    return HttpResponseRedirect(oauth_url)

def CallbackView(request):
    try:
        # Get user credentials
        credentials = google_apis_oauth.get_crendentials_from_callback(
            request,
            JSON_FILEPATH,
            SCOPES,
            REDIRECT_URI
        )

        # Stringify credentials for storing them in the DB
        stringified_token = google_apis_oauth.stringify_credentials(
            credentials)

        # Store the credentials safely in the DB
        request.session ['key'] = stringified_token

        # Now that you have stored the user credentials you
        # can redirect user to your main application.
        messages.success(request, "Logged in successfully." )
        return HttpResponseRedirect(reverse('events'))
    except google_apis_oauth.exceptions.InvalidLoginException:
        messages.warning(request, "Invalid login." )
        # This exception is raised when there is an inavlid
        # request to this callback uri.
