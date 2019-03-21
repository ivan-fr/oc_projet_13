import urllib.parse

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from swingtime.models import EventType
from catalogue.models import Meeting, Place
from ventes.models import Commande, CommandeMeeting


class AuthenticatedViewsTestCase(TestCase):
    """ test of authenticated views """

    # run before each test.
    def setUp(self):
        self.credentials = {'username': 'a-user', 'password': 'password'}
        self.user = User.objects.create_user(**self.credentials)
        self.client.login(**self.credentials)

        self.eventtype, _ = EventType.objects.get_or_create(
            label='a label'
        )

        self.place, _ = Place.objects.get_or_create(
            name='a place',
            space_available=30,
            street='a street',
            city='a city',
            postal_code='75000',
            department=75
        )

        self.meeting, _ = Meeting.objects.get_or_create(
            pk=8,
            place=self.place,
            price=10.0,
            title="a title",
            event_type=self.eventtype,
            recurrences='RRULE:FREQ=WEEKLY;UNTIL=20190430T220000Z;'
                        'BYDAY=SA;BYHOUR=18;BYMINUTE=30'
        )

    def tearDown(self):
        self.client.logout()

    def test_get_CommandeFormsetView(self):
        response = self.client.get(
            reverse('ventes:commande-formset'),
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

        self.assertIsNotNone(response.context['formset'])
        self.assertIsNotNone(response.context['meetings'])
        self.assertIsNotNone(response.context['sign'])
        self.assertTemplateUsed(response, 'ventes/commande_formset.html')

    def test_post_CommandeFormsetView(self):
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '3',
            'form-0-name': 'Chéri, on se dit tout !',
            'form-0-date': '23/03/2019 18:30',
            'form-0-id': str(self.meeting.pk),
            'form-0-count': '1',
            'form-sign': 'W3siaWQiOiI4IiwibmFtZSI6IkNoXHUwMGU5cmksIG9uIHNlIGRp'
                         'dCB0b3V0ICEiLCJkYXRlIjoiMjMvMDMvMjAxOSAxODozMCIsImN'
                         'vdW50IjoxLCJwcmljZSI6MTV9XQ:1h5W8N:E-5xTOz6BHI1EZ0'
                         'xvRLnVfetSPk'
        }

        commande_count = Commande.objects.count()
        commande_commande_meeting_count = CommandeMeeting.objects.count()

        response = self.client.post(reverse('ventes:commande-formset'), data)

        commande_count_new = Commande.objects.count()
        commande_commande_meeting_count_new = CommandeMeeting.objects.count()

        self.assertEqual(commande_count, commande_count_new - 1)
        self.assertEqual(commande_commande_meeting_count,
                         commande_commande_meeting_count_new - 1)

        commande = Commande.objects.all().first()

        self.assertRedirects(response, reverse(
            'ventes:show-commande',
            kwargs={
                'commande_pk': commande.pk,
            }) + '?' + urllib.parse.urlencode({
            'from_accepted_command': True
        }))

    def test_get_CommandeTemplateView(self):
        response = self.client.get(reverse('ventes:commande'))
        self.assertTemplateUsed(response, 'ventes/commande.html')
