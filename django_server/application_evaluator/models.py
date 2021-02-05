import secrets

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
        if user.is_staff:
            return cls.objects.all()
        return cls.objects.filter(applications__evaluating_organizations__users=user).distinct()

    def applications_for_evaluator(self, user):
        if user.is_staff:
            return self.applications.all()
        return self.applications.filter(evaluating_organizations__users=user).distinct()

    def clone(self):
        copy = ApplicationRound.objects.create(name=f'Copy of {self.name}')
        groupCopies = {}
        for group in self.criterion_groups.all():
            groupCopies[group.id] = copy.criterion_groups.create(
                name=group.name, threshold=group.threshold, order=group.order, abbr=group.abbr)
        for group in self.criterion_groups.all():
            groupCopies[group.id].parent = groupCopies.get(group.parent_id, None)
            groupCopies[group.id].save()
        for criterion in self.criteria.all():
            copy.criteria.create(name=criterion.name, group=groupCopies[criterion.group_id],
                                 public=criterion.public, order=criterion.order, weight=criterion.weight)


def upload_round_attachment_to(instance, filename):
    return f'application_round_attachments/{secrets.token_hex(32)}/{filename}'


class ApplicationRoundAttachment(NamedModel):
    application_round = models.ForeignKey(ApplicationRound, related_name='attachments', on_delete=models.CASCADE)
    attachment = models.FileField(upload_to=upload_round_attachment_to, max_length=256)


class CriterionGroup(NamedModel):
    """
    Grouping element for the evaluation criteria. Can be used to create a hierarchy of any depth.
    """
    abbr = models.CharField(max_length=8, blank=True)
    application_round = models.ForeignKey(ApplicationRound, related_name='criterion_groups', on_delete=models.CASCADE)
    parent = models.ForeignKey('CriterionGroup', related_name='child_groups',
                               on_delete=models.CASCADE, null=True, blank=True)
    order = models.IntegerField(default=0)
    threshold = models.FloatField(blank=True, null=True)


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


def organization(user):
    if not hasattr(user, '_organization'):
        orgs = list(user.organizations.all())
        user._organization = orgs[0] if len(orgs) else None
    return user._organization


User.organization = property(organization)


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
        return Score.filter_for_evaluator(self.scores.all(), user)

    def comments_for_evaluator(self, user):
        return Comment.filter_for_evaluator(self.comments.all(), user)

    @classmethod
    def applications_for_evaluator(cls, user):
        if user.is_staff:
            return cls.objects.all()
        return cls.objects.filter(evaluating_organizations__users=user).distinct()


def upload_attachment_to(instance, filename):
    return f'application_attachments/{secrets.token_hex(32)}/{filename}'


class ApplicationAttachment(NamedModel):
    application = models.ForeignKey(Application, related_name='attachments', on_delete=models.CASCADE)
    attachment = models.FileField(upload_to=upload_attachment_to, max_length=256)

    def save(self, **kwargs):
        if self.attachment and not self.name:
            self.name = self.attachment.name
        return super().save(**kwargs)


class EvaluationModel(TimestampedModel):
    """
    Model used for evaluating applications
    """
    application = models.ForeignKey(Application, related_name='%(class)ss', on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, related_name='%(class)ss', on_delete=models.CASCADE)
    evaluator = models.ForeignKey(User, related_name='%(class)ss', on_delete=models.CASCADE)

    class Meta:
        abstract = True

    @staticmethod
    def filter_for_evaluator(instances, user):
        if user.is_staff:
            return instances
        if not user.organization:
            return []
        return [s for s in instances
                if s.evaluator.organization and s.evaluator.organization == user.organization]


class Score(EvaluationModel):
    score = models.FloatField(default=0)


class Comment(EvaluationModel):
    comment = models.TextField(blank=True)
