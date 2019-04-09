from django.test import TestCase
from django.urls import reverse
from swingtime.models import EventType
from catalogue.models import Place, Meeting


class ViewTestCase(TestCase):

    def test_get_index(self):
        """ test of get in index view """

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['root_events_types'])
        self.assertIsNotNone(response.context['departments'])
        self.assertIsNotNone(response.context['filled_departments'])
        self.assertTrue(response.context['index'])
        self.assertTemplateUsed(response, 'catalogue/index_list.html')

    def test_get_event_type(self):
        eventtype = EventType.objects.create(
            label="bonjour"
        )

        response = self.client.get(
            reverse('catalogue:show-eventtype',
                    kwargs={
                        'event_type_pk': eventtype.pk
                    })
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['root_events_types'])
        self.assertIsNotNone(response.context['eventtype'])
        self.assertIsNotNone(response.context['selected_eventtype'])
        self.assertTemplateUsed(response, 'catalogue/meeting_list.html')

    def test_get_meeting(self):
        eventtype = EventType.objects.create(
            label="bonjour"
        )

        place = Place.objects.create(
            department='75',
            name='test',
            space_available=100,
            street='test',
            city='paris',
            postal_code='75000'
        )

        meeting = Meeting.objects.create(
            price=10,
            place=place,
            title='a test',
            event_type=eventtype
        )

        response = self.client.get(
            reverse('catalogue:show-meeting',
                    kwargs={
                        'meeting_pk': meeting.pk
                    })
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['root_events_types'])
        self.assertIsNotNone(response.context['breadcrumb'])
        self.assertIsNotNone(response.context['eventtype'])
        self.assertTemplateUsed(response, 'catalogue/meeting_detail.html')
