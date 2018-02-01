from django.test import TestCase, Client
from django.contrib.auth.models import User


class BaseTestCase(TestCase):

    MOCK_USERNAME = 'admin'
    MOCK_EMAIL = 'admin@example.com'
    MOCK_PASSWORD = 'secret'

    def setUp(self):
        self.client = Client()
        User.objects.create_superuser(self.MOCK_USERNAME, self.MOCK_EMAIL, self.MOCK_PASSWORD)

    def login(self):
        return self.client.post('/admin/login/', {'username': self.MOCK_USERNAME, 'password': self.MOCK_PASSWORD})

    def logout(self):
        return self.client.get('/admin/logout/')
