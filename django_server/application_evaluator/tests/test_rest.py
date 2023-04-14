from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from application_evaluator import models


class RestTests(APITestCase):
    maxDiff = None

    def test_application_rounds_not_logged_in(self):
        # Given no logged in user
        # When requesting the application round list
        url = reverse('application_round-list')
        response = self.client.get(url)

        # Then a 401 Unauthorized response is received
        self.assertEqual(response.status_code, 401)

    def test_application_rounds_when_none_allocated(self):
        # Given a logged in user that does not belong to any organization with allocated applications
        evaluator = User.objects.create(username="evaluator")
        self.client.force_login(evaluator)
        app_round = models.ApplicationRound.objects.create(name='AI4Cities')
        app = app_round.applications.create(name='SkyNet')
        criterion1 = app_round.criteria.create(name='Goodness', weight=1)

        # When requesting the application round list
        url = reverse('application_round-list')
        response = self.client.get(url)

        # Then an empty list is received
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_application_rounds_when_not_published(self):
        # Given a logged in user that belongs to an organization with allocated applications only in unpublished rounds
        evaluator = User.objects.create(username="evaluator")
        organization = evaluator.organizations.create(name='Helsinki')
        self.client.force_login(evaluator)
        app_round = models.ApplicationRound.objects.create(name='AI4Cities')
        app = app_round.applications.create(name='SkyNet')
        criterion1 = app_round.criteria.create(name='Goodness', weight=1)
        app.evaluating_organizations.add(organization)

        # When requesting the application round list
        url = reverse('application_round-list')
        response = self.client.get(url)

        # Then an empty list is received
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_application_rounds(self):
        # Given a logged in user that belongs to an organization with allocated applications
        evaluator = User.objects.create(username="evaluator")
        self.client.force_login(evaluator)
        app_round = models.ApplicationRound.objects.create(name='AI4Cities', published=True)
        app = app_round.applications.create(name='SkyNet')
        criterion1 = app_round.criteria.create(name='Goodness', weight=1)
        organization = evaluator.organizations.create(name='Helsinki')
        app.evaluating_organizations.add(organization)

        # And given that applications have received scores from both within and outside of the user's organization
        evaluator2 = User.objects.create(username="evaluator2")
        organization2 = evaluator2.organizations.create(name='Tallinn')
        app.evaluating_organizations.add(organization2)
        score1 = app.scores.create(evaluator=evaluator, score=5, criterion=criterion1)
        score2 = app.scores.create(evaluator=evaluator2, score=5, criterion=criterion1)

        # And some scores for non-public criteria
        criterion2 = app_round.criteria.create(name='Wellness', weight=1, public=False)
        score3 = app.scores.create(evaluator=evaluator2, score=5, criterion=criterion2)

        # When requesting the application round list
        url = reverse('application_round-list')
        response = self.client.get(url)

        # Then the application rounds of the allocated applications are received, along with public scores given
        # by the user's organization
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{
            'id': app_round.id,
            'applications': [{
                'id': app.id,
                'name': 'SkyNet',
                'description': '',
                'evaluating_organizations': ['Helsinki', 'Tallinn'],
                'comments': [],
                'attachments': [],
                'approved': False,
                'approved_by': None,
                'scores': [{
                    'id': score1.id,
                    'application': app.id,
                    'score': 5.0,
                    'criterion': criterion1.id,
                    'evaluator': {
                        'id': evaluator.id,
                        'first_name': '',
                        'last_name': '',
                        'organization': 'Helsinki',
                        'username': 'evaluator'}
                }]
            }],
            'criteria': [{'name': 'Goodness', 'group': None, 'id': criterion1.id, 'weight': 1.0}],
            'criterion_groups': [],
            'attachments': [],
            'admin': None,
            'submitted_organizations': [],
            'description': '',
            'name': 'AI4Cities',
            'evaluators': [],
            'scoring_completed': False,
            'scoring_model': 'Evaluators average',
        }])

    def test_application_rounds_without_organizations(self):
        # Given a logged in user who is allocated as evaluator for an application round
        evaluator = User.objects.create(username="evaluator")
        self.client.force_login(evaluator)
        app_round = models.ApplicationRound.objects.create(name='AI4Cities', published=True)
        app = app_round.applications.create(name='SkyNet')
        criterion1 = app_round.criteria.create(name='Goodness', weight=1)
        app_round.evaluators.add(evaluator)

        # And given that applications have received scores from both the user and others
        evaluator2 = User.objects.create(username="evaluator2")
        app_round.evaluators.add(evaluator2)
        score1 = app.scores.create(evaluator=evaluator, score=5, criterion=criterion1)
        score2 = app.scores.create(evaluator=evaluator2, score=5, criterion=criterion1)

        # When requesting the application round list
        url = reverse('application_round-list')
        response = self.client.get(url)

        # Then the allocated application rounds are received, along with the scores given
        # by the user
        self.assertEqual(response.status_code, 200)
        rounds = response.json()
        self.assertEqual(len(rounds), 1)
        applications = rounds[0]['applications']
        self.assertEqual(len(applications), 1)
        self.assertEqual(len(applications[0]['scores']), 1)

    def test_submit_organization_scores_when_none_given(self):
        # Given a logged in user that belongs to an organization with allocated applications
        # in an application round but no scores given
        evaluator = User.objects.create(username="evaluator")
        self.client.force_login(evaluator)
        app_round = models.ApplicationRound.objects.create(name='AI4Cities')
        app = app_round.applications.create(name='SkyNet')
        criterion1 = app_round.criteria.create(name='Goodness', weight=1)
        organization = evaluator.organizations.create(name='Helsinki')
        app.evaluating_organizations.add(organization)

        # When requesting to submit the scores for the round
        url = reverse('application_round-submit', kwargs={'pk': app_round.id})
        response = self.client.post(url)

        # Then a 404 response is received
        self.assertEqual(response.status_code, 404)

    def test_submit_organization_scores(self):
        # Given a logged in user that belongs to an organization with allocated applications
        # in an application round
        evaluator = User.objects.create(username="evaluator")
        self.client.force_login(evaluator)
        app_round = models.ApplicationRound.objects.create(name='AI4Cities', published=True)
        app = app_round.applications.create(name='SkyNet')
        criterion1 = app_round.criteria.create(name='Goodness', weight=1)
        organization = evaluator.organizations.create(name='Helsinki')
        app.evaluating_organizations.add(organization)

        # And given that applications have received scores for all criteria by the user's organization
        score1 = app.scores.create(evaluator=evaluator, score=5, criterion=criterion1)

        # When requesting to submit the scores for the round
        url = reverse('application_round-submit', kwargs={'pk': app_round.id})
        response = self.client.post(url)

        # Then a 200 response is received
        self.assertEqual(response.status_code, 200)

        # And the round is marked submitted by the user's organization
        self.assertEqual([o.name for o in app_round.submitted_organizations.all()], ['Helsinki'])

        # And subsequent attempts to change scores by that organization fail:
        response = self.client.delete(reverse('score-detail', kwargs={'pk': score1.id}))
        self.assertEqual(response.status_code, 404)

        # And subsequent requests for applications in the submitted round return all scores
        # from all organizations which have submitted their scores:
        evaluator2 = User.objects.create(username="evaluator2")
        organization2 = evaluator2.organizations.create(name='Tallinn')
        app.evaluating_organizations.add(organization2)
        score2 = app.scores.create(evaluator=evaluator2, score=5, criterion=criterion1)
        app_round.submittals.create(user=evaluator2, organization=organization2)

        url = reverse('application-detail', kwargs={'pk': app.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['scores']), 2)

    def test_approve_application(self):
        # Given a logged in user that belongs to an organization with allocated applications
        evaluator = User.objects.create(username="evaluator")
        self.client.force_login(evaluator)
        app_round = models.ApplicationRound.objects.create(name='AI4Cities', published=True)
        app = app_round.applications.create(name='SkyNet')
        criterion1 = app_round.criteria.create(name='Goodness', weight=1)
        organization = evaluator.organizations.create(name='Helsinki')
        app.evaluating_organizations.add(organization)

        # When a request is made to approve the application
        url = reverse('application-approve', kwargs={'pk': app.id})
        response = self.client.post(url)

        # Then a 200 response is received
        self.assertEqual(response.status_code, 200)

        # And the application is marked as approved
        app.refresh_from_db()
        self.assertTrue(app.approved)

        # And the application is marked as approved_by the user
        self.assertEqual(app.approved_by_id, evaluator.id)

        # And when a subsequent request is made to unapprove the application
        url = reverse('application-unapprove', kwargs={'pk': app.id})
        response = self.client.post(url)

        # Then a 200 response is received
        self.assertEqual(response.status_code, 200)

        # And the application is marked as not approved
        app.refresh_from_db()
        self.assertFalse(app.approved)

        # And the application approved_by is empty
        self.assertIsNone(app.approved_by)
