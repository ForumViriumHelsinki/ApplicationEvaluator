from django.contrib.auth.models import User
from django.db import models


class Model(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return (self.id and f'{self.__class__.__name__}({self.id})') or f'New {self.__class__.__name__}'


class TimestampedModel(Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NamedModel(Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name or super().__str__()

    class Meta:
        abstract = True


class ApplicationRound(NamedModel):
    """
    Application round (e.g. request for tenders/quotes).

    All applications in the same round will be evaluated using the same criteria.
    """
    def total_weight(self):
        """
        Return the total weight of all criteria in this Application Round.
        """
        return sum(c.weight for c in self.criteria.all())

    @classmethod
    def rounds_for_evaluator(cls, user):
        return cls.objects.filter(applications__evaluating_organizations__users=user).distinct()

    def applications_for_evaluator(self, user):
        return self.applications.filter(evaluating_organizations__users=user).distinct()


class CriterionGroup(NamedModel):
    """
    Grouping element for the evaluation criteria. Can be used to create a hierarchy of any depth.
    """
    application_round = models.ForeignKey(ApplicationRound, related_name='criterion_groups', on_delete=models.CASCADE)
    parent = models.ForeignKey('CriterionGroup', related_name='child_groups',
                               on_delete=models.CASCADE, null=True, blank=True)
    order = models.IntegerField(default=0)


class Criterion(NamedModel):
    """
    Criterion by which the applications are evaluated.
    """
    application_round = models.ForeignKey(ApplicationRound, related_name='criteria', on_delete=models.CASCADE)
    group = models.ForeignKey(CriterionGroup, related_name='criteria', on_delete=models.CASCADE, null=True, blank=True)
    public = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    weight = models.FloatField(default=0)


class Organization(NamedModel):
    users = models.ManyToManyField(User, blank=True, related_name='organizations')


class Application(NamedModel):
    application_round = models.ForeignKey(ApplicationRound, related_name='applications', on_delete=models.CASCADE)
    evaluating_organizations = models.ManyToManyField(Organization, related_name='applications_to_evaluate')

    def score(self):
        total = 0
        for criterion in self.application_round.criteria.all():
            scores = [s for s in self.scores.all() if s.criterion_id == criterion.id]
            if len(scores):
                mean = sum(s.score for s in scores) / len(scores)
                total += mean * criterion.weight
        return total / self.application_round.total_weight()

    def can_be_evaluated_by(self, user):
        return self.evaluating_organizations.filter(users=user).exists()

    def scores_for_evaluator(self, user):
        return self.scores.filter(evaluator__organizations__users=user, criterion__public=True).distinct()

    @classmethod
    def applications_for_evaluator(cls, user):
        return cls.objects.filter(evaluating_organizations__users=user).distinct()


class Score(TimestampedModel):
    application = models.ForeignKey(Application, related_name='scores', on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, related_name='scores', on_delete=models.CASCADE)
    evaluator = models.ForeignKey(User, related_name='scores', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
