from django.urls import reverse
from django.urls import resolve
from django.test import TestCase
from .views import home, calendar_events
from .models import Calendar

class HomeTests(TestCase):
    def setUp(self):
        self.calendar = Calendar.objects.create(name='Sophia')
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func, home)

    def test_home_view_contains_link_to_events_page(self):
        calendar_events_url = reverse('calendar_events', kwargs={'pk': self.calendar.pk})
        self.assertContains(self.response, 'href="{0}"'.format(calendar_events_url))

class CalendarEventsTests(TestCase):
    def setUp(self):
        Calendar.objects.create(name='Sophia')

    def test_calendar_events_view_success_status_code(self):
        url = reverse('calendar_events', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_calendar_events_view_not_found_status_code(self):
        url = reverse('calendar_events', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_calendar_events_url_resolves_calendar_events_view(self):
        view = resolve('/calendars/1/')
        self.assertEquals(view.func, calendar_events)

    def test_calendar_events_view_contains_link_back_to_homepage(self):
        calendar_events_url = reverse('calendar_events', kwargs={'pk':1})
        response = self.client.get(calendar_events_url)
        homepage_url = reverse('home')
        self.assertContains(response, 'href="{0}"'.format(homepage_url))
