from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.core import mail

from application_evaluator import models


class ModelTests(TestCase):
    def test_application_score(self):
        app_round = models.ApplicationRound.objects.create(name='AI4Cities')
        app = app_round.applications.create(name='SkyNet')
        criterion1 = app_round.criteria.create(name='Goodness', weight=1)

        evaluator = User.objects.create(username="evaluator")

        # Given an application with no scores
        # When the total score is requested
        # Then 0 is returned
        self.assertEqual(app.score(), 0)

        # Given an application with one criterion and one score
        app.scores.create(criterion=criterion1, evaluator=evaluator, score=5)
        # When the total score is requested
        # Then the given score is returned
        self.assertEqual(app.score(), 5)

        # Given an application with scores given for only some of the criteria
        criterion2 = app_round.criteria.create(name='Awesomeness', weight=2)
        # When the total score is requested
        # Then the weighed average of scores is given, with 0 used as the score for criteria missing scores
        self.assertEqual(app.score(), 5 / 3)

        # Given an application with several criteria and scores for all of them
        app.scores.create(criterion=criterion2, evaluator=evaluator, score=3)
        # When the total score is requested
        # Then the weighed average of scores is given
        self.assertEqual(app.score(), (2*3 + 5) / 3)

        # Given an application with several criteria and multiple scores for the same criterion
        evaluator2 = User.objects.create(username="evaluator2")
        app.scores.create(criterion=criterion2, evaluator=evaluator2, score=4)
        # When the total score is requested
        # Then the scores for each separate criterion is averaged before the total weighed average is computed
        self.assertEqual(app.score(), (2*3.5 + 5) / 3)


class RestTests(APITestCase):
    def test_application_rounds(self):
        # Given no logged in user
        # When requesting the application round list
        url = reverse('application_round-list')
        response = self.client.get(url)

        # Then a 401 Unauthorized response is received
        self.assertEqual(response.status_code, 401)

        # Given a logged in user that does not belong to any organization with allocated applications
        evaluator = User.objects.create(username="evaluator")
        self.client.force_login(evaluator)
        app_round = models.ApplicationRound.objects.create(name='AI4Cities')
        app = app_round.applications.create(name='SkyNet')
        criterion1 = app_round.criteria.create(name='Goodness', weight=1)

        # When requesting the application round list
        response = self.client.get(url)
        # Then an empty list is received
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

        # Given a logged in user that belongs to an organization with allocated applications
        organization = evaluator.organizations.create(name='Helsinki')
        app.evaluating_organizations.add(organization)

        # And given that applications have received scores from both within and outside of the user's organization
        evaluator2 = User.objects.create(username="evaluator2")
        score1 = app.scores.create(evaluator=evaluator, score=5, criterion=criterion1)
        score2 = app.scores.create(evaluator=evaluator2, score=5, criterion=criterion1)

        # And some scores for non-public criteria
        criterion2 = app_round.criteria.create(name='Wellness', weight=1, public=False)
        score3 = app.scores.create(evaluator=evaluator2, score=5, criterion=criterion2)

        # When requesting the application round list
        response = self.client.get(url)

        # Then the application rounds of the allocated applications are received, along with public scores given
        # by the user's organization
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{
            'id': app_round.id,
            'applications': [{
                'id': app.id,
                'name': 'SkyNet',
                'evaluating_organizations': ['Helsinki'],
                'comments': [],
                'scores': [{
                    'id': score1.id,
                    'application': app.id,
                    'score': 5,
                    'criterion': criterion1.id,
                    'evaluator': {
                        'id': evaluator.id,
                        'first_name': '',
                        'last_name': '',
                        'organization': 'Helsinki',
                        'username': 'evaluator'}
                }]
            }],
            'criteria': [{'name': 'Goodness', 'group': None, 'id': criterion1.id, 'weight': 1}],
            'criterion_groups': [],
            'name': 'AI4Cities'
        }])


class RestAuthTests(APITestCase):
    def test_reset_password(self):
        user = User.objects.create(username='user', email='some@user.com')
        response = self.client.post('/rest-auth/password/reset/', {'email': user.email})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
