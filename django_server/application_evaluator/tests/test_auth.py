from django.contrib.auth.models import User
from django.core import mail
from rest_framework.test import APITestCase


class RestAuthTests(APITestCase):
    def test_reset_password(self):
        user = User.objects.create(username="user", email="some@user.com")
        response = self.client.post("/rest-auth/password/reset/", {"email": user.email})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
