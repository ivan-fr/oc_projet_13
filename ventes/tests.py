import urllib.parse
import datetime

from six import text_type

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import signing
from django.core.signing import Signer
from django.utils import timezone

from paypal.standard.ipn.models import PayPalIPN

from swingtime.models import EventType
from catalogue.models import Meeting, Place
from ventes.models import Commande, CommandeMeeting
from ventes.signals import payment_notification
from paypal.standard.ipn.signals import valid_ipn_received

CHARSET = "windows-1252"
IPN_POST_PARAMS = {
    "protection_eligibility": b"Ineligible",
    "last_name": b"User",
    "txn_id": b"51403485VH153354B",
    "receiver_email": settings.PAYPAL_RECEIVER_EMAIL,
    "payment_status": b"Completed",
    "payment_gross": b"10.00",
    "tax": b"0.00",
    "residence_country": b"US",
    "invoice": b"0004",
    "payer_status": b"verified",
    "txn_type": b"express_checkout",
    "handling_amount": b"0.00",
    "payment_date": b"23:04:06 Feb 02, 2009 PST",
    "first_name": b"J\xF6rg",
    "item_name": b"",
    "charset": CHARSET.encode('ascii'),
    "custom": None,
    "notify_version": b"2.6",
    "transaction_subject": b"",
    "test_ipn": b"1",
    "item_number": b"",
    "receiver_id": b"258DLEHY2BDK6",
    "payer_id": b"BN5JZ2V7MLEV4",
    "verify_sign": b"An5ns1Kso7MWUdW4ErQKJJJ4qi4-AqdZy6dD.sGO3sDhTf1wAbuO2IZ7",
    "payment_fee": b"0.59",
    "mc_fee": b"0.59",
    "mc_currency": b"EUR",
    "shipping": b"0.00",
    "payer_email": b"bishan_1233269544_per@gmail.com",
    "payment_type": b"instant",
    "mc_gross": b"10.00",
    "quantity": b"1",
}


class AuthenticatedViewsTestCase(TestCase):
    """ test of authenticated views """

    # run before each test.
    def setUp(self):
        self.credentials = {'username': 'a-user', 'password': 'password'}
        self.supercredentials = {'username': 'super', 'password': 'super', 'email': 'super@yahoo.com'}
        User.objects.create_superuser(**self.supercredentials)
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

        self.commande, _ = Commande.objects.get_or_create(
            user=self.user
        )

        self.meeting, _ = Meeting.objects.get_or_create(
            pk=7,
            place=self.place,
            price=10.0,
            title="a title",
            event_type=self.eventtype)

        self.old_postback = PayPalIPN._postback
        PayPalIPN._postback = lambda _self: b"VERIFIED"

    def tearDown(self):
        PayPalIPN._postback = self.old_postback

    def test_get_CommandeFormsetView(self):
        response = self.client.get(
            reverse('ventes:commande-formset'),
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

        self.assertIsNotNone(response.context['formset'])
        self.assertIsNotNone(response.context['meetings'])
        self.assertIsNotNone(response.context['sign'])
        self.assertTemplateUsed(response, 'ventes/commande_formset.html')
        self.assertEqual(response.status_code, 200)

    def test_post_CommandeFormsetView(self):
        next_monday = datetime.datetime.now()
        next_monday += datetime.timedelta(days=-next_monday.weekday(), weeks=1)

        second_next_monday = next_monday + datetime.timedelta(weeks=1)

        meeting, _ = Meeting.objects.get_or_create(
            pk=8,
            place=self.place,
            price=10.0,
            title="a title",
            event_type=self.eventtype,
            recurrences='RRULE:FREQ=WEEKLY;UNTIL='
                        + second_next_monday.strftime('%Y%m%d') +
                        ';BYDAY=MO;BYHOUR=' + next_monday.strftime('%H') +
                        ';BYMINUTE=' + next_monday.strftime('%M')
        )

        sign = signing.dumps([{'name': meeting.title,
                               'date': next_monday.strftime('%d/%m/%Y %H:%M'),
                               'id': str(meeting.pk),
                               'count': '1'}])

        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '3',
            'form-0-name': meeting.title,
            'form-0-date': next_monday.strftime('%d/%m/%Y %H:%M'),
            'form-0-id': str(meeting.pk),
            'form-0-count': '1',
            'form-sign': sign
        }

        commande_count = Commande.objects.count()
        commande_commande_meeting_count = CommandeMeeting.objects.count()

        response = self.client.post(reverse('ventes:commande-formset'), data)

        commande_count_new = Commande.objects.count()
        commande_commande_meeting_count_new = CommandeMeeting.objects.count()

        self.assertEqual(commande_count, commande_count_new - 1)
        self.assertEqual(commande_commande_meeting_count,
                         commande_commande_meeting_count_new - 1)

        commande = Commande.objects.all().last()

        self.assertRedirects(response, reverse(
            'ventes:show-commande',
            kwargs={
                'commande_pk': commande.pk,
            }) + '?' + urllib.parse.urlencode({'from_accepted_command': True}))
        self.assertEqual(response.status_code, 302)

    def test_get_CommandeTemplateView(self):
        response = self.client.get(reverse('ventes:commande'))
        self.assertTemplateUsed(response, 'ventes/commande.html')
        self.assertEqual(response.status_code, 200)

    def test_get_CommandeArchiveView(self):
        response = self.client.get(reverse('ventes:commandes'))
        self.assertTemplateUsed(response, 'ventes/commande_archive.html')
        self.assertEqual(response.status_code, 200)

    def test_get_CommandeYearArchiveView(self):
        now = datetime.datetime.now()
        response = self.client.get(
            reverse(
                'ventes:commandes-year',
                kwargs={'year': now.year}
            )
        )
        self.assertTemplateUsed(response, 'ventes/commande_archive_year.html')
        self.assertEqual(response.status_code, 200)

    def test_get_CommandeMonthArchiveView(self):
        now = datetime.datetime.now()
        response = self.client.get(
            reverse(
                'ventes:commandes-month',
                kwargs={
                    'year': now.year,
                    'month': now.month
                }
            )
        )
        self.assertTemplateUsed(response, 'ventes/commande_archive_month.html')
        self.assertEqual(response.status_code, 200)

    def test_get_CommandeView(self):
        response = self.client.get(
            reverse('ventes:show-commande',
                    kwargs={'commande_pk': self.commande.pk})
        )

        self.assertTemplateUsed(response, 'ventes/commande_detail.html')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['paypal_form'])
        self.assertIsNotNone(response.context['object'])
        self.assertIsNotNone(response.context['from_accepted_command'])

    def test_get_CommandePaymentSuccesTemplateView(self):
        response = self.client.get(
            reverse('ventes:commande-success',
                    kwargs={'commande_pk': self.commande.pk}))
        self.assertTemplateUsed(response, 'ventes/commande_success.html')
        self.assertEqual(response.status_code, 200)

    def paypal_post(self, params):
        """
        Does an HTTP POST the way that PayPal does, using the params given.
        """

        # We build params into a bytestring ourselves, to avoid some encoding
        # processing that is done by the test client.
        def cond_encode(v):
            if isinstance(v, text_type):
                return v.encode(CHARSET)
            else:
                return v

        byte_params = {cond_encode(k): cond_encode(v) for k, v in
                       params.items()}
        post_data = urllib.parse.urlencode(byte_params)
        return self.client.post(reverse('paypal-ipn'),
                                post_data,
                                content_type='application/x-www-form-urlencoded'
                                )

    def test_signal_payment(self):
        # Check the signal was sent. These get
        # lost if they don't reference self.
        commande_meeting, _ = CommandeMeeting.objects.get_or_create(
            to_meeting=self.meeting,
            from_commande=self.commande,
            quantity=1,
            date_meeting=datetime.datetime(2009, 5, 3, 7, 4, 6,
                                           tzinfo=timezone.utc
                                           if settings.USE_TZ else None)
        )

        valid_ipn_received.connect(payment_notification)

        signer = Signer()

        IPN_POST_PARAMS['custom'] = signer.sign(self.commande.pk)

        response = self.paypal_post(IPN_POST_PARAMS)
        self.assertEqual(response.status_code, 200)
        ipns = PayPalIPN.objects.all()
        self.assertEqual(len(ipns), 1)

        commande_meeting.refresh_from_db()
        self.commande.refresh_from_db()

        self.assertTrue(commande_meeting.qrcode is not None)
        self.assertTrue(self.commande.payment_status)

    def test_TurnoverView(self):
        self.client.logout()
        self.client.login(**self.supercredentials)
        response = self.client.get(
            reverse('ventes:commandes-turnover')
        )

        self.assertTemplateUsed(response, 'ventes/turnover.html')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['by_month'])
