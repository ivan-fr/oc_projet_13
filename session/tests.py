from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class AuthenticatedViewsTestCase(TestCase):
    """ test of authenticated views """

    # run before each test.
    def setUp(self):
        self.credentials = {'username': 'a-user', 'password': 'password'}
        self.credentials_2 = {'username': 'a-user_2', 'password': 'password_2'}
        self.user = User.objects.create_user(**self.credentials)
        User.objects.create_user(**self.credentials_2)
        self.client.login(**self.credentials)

    def test_login_redirect(self):
        """test of the login redirection"""

        self.client.logout()
        response = self.client.post(reverse('session:login'), self.credentials)
        self.assertRedirects(response, reverse('index'))

    def test_get_WhoIsOnlineView(self):
        response = self.client.get(
            reverse('session:whoisonline')
        )

        self.assertTemplateUsed(response, 'auth/user_list.html')
        self.assertEqual(response.status_code, 200)

    def test_get_ThreadView(self):
        response = self.client.get(
            reverse('session:thread', kwargs={
                'username': 'a-user_2'
            })
        )

        self.assertTemplateUsed(response, 'session/thread_detail.html')
        self.assertEqual(response.status_code, 200)

    def test_get_InboxView(self):
        response = self.client.get(
            reverse('session:inbox')
        )

        self.assertTemplateUsed(response, 'session/thread_list.html')
        self.assertEqual(response.status_code, 200)
