from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class AuthenticatedViewsTestCase(TestCase):
    """ test of authenticated views """

    # run before each test.
    def setUp(self):
        self.credentials = {'username': 'a-user', 'password': 'password'}
        self.user = User.objects.create_user(**self.credentials)

    def test_login_redirect(self):
        """test of the login redirection"""

        self.client.logout()
        response = self.client.post(reverse('session:login'), self.credentials)
        self.assertRedirects(response, reverse('index'))
