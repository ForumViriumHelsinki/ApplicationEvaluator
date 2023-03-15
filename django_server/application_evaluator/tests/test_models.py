from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.test import TestCase

from application_evaluator import models


class ModelTests(TestCase):
    def test_application_score(self):
        app_round = models.ApplicationRound.objects.create(name='AI4Cities')
        app = app_round.applications.create(name='SkyNet')
        criterion1 = app_round.criteria.create(name='Goodness', weight=1)

        evaluator = User.objects.create(username="evaluator")
        org = evaluator.organizations.create(name='Org')

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
        self.assertEqual(app.score(), (2 * 3 + 5) / 3)

        # Given an application with several criteria and multiple scores for the same criterion
        evaluator2 = User.objects.create(username="evaluator2")
        org2 = evaluator2.organizations.create(name='Org2')
        app.scores.create(criterion=criterion2, evaluator=evaluator2, score=4)
        # When the total score is requested
        # Then the scores for each separate criterion is averaged before the total weighed average is computed
        self.assertEqual(app.score(), (2 * 3.5 + 5) / 3)
