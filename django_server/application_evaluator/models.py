import csv
import secrets
import zipfile

from django.contrib.auth.models import User
from django.core.files import File
from django.db import models
from django.utils.safestring import mark_safe


class Model(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return (self.id and f"{self.__class__.__name__}({self.id})") or f"New {self.__class__.__name__}"


class TimestampedModel(Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NamedModel(Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name or super().__str__()

    class Meta:
        abstract = True


def description_field():
    return models.TextField(
        blank=True,
        help_text=mark_safe(
            "Content that will be shown to the evaluators in the public UI. May use "
            + '<a href="https://www.markdownguide.org/basic-syntax/" target="_blank">Markdown</a>'
            + " for e.g. links and formatting."
        ),
    )


class ApplicationRound(NamedModel):
    """
    Application round (e.g. request for tenders/quotes).

    All applications in the same round will be evaluated using the same criteria.
    """

    submitted_organizations = models.ManyToManyField(
        "Organization", through="ApplicationRoundSubmittal", related_name="submitted_application_rounds", blank=True
    )
    published = models.BooleanField(default=False)
    city = models.CharField(max_length=64, blank=True)
    description = description_field()
    evaluators = models.ManyToManyField(User, related_name="evaluated_application_rounds", blank=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="administered_application_rounds", null=True)
    scoring_model = models.CharField(
        max_length=32,
        default="Evaluators average",
        choices=((x, x) for x in ["Evaluators average", "Organizations average"]),
    )
    scoring_completed = models.BooleanField(default=False, help_text="Set by an admin to close scoring for this round.")

    def total_weight(self):
        """
        Return the total weight of all criteria in this Application Round.
        """
        return sum(c.weight for c in self.criteria.all())

    @classmethod
    def rounds_for_evaluator(cls, user):
        if user.is_staff:
            return cls.objects.all()
        return (
            cls.objects.filter(published=True)
            .filter(
                models.Q(applications__evaluating_organizations__users=user)
                | models.Q(evaluators=user)
                | models.Q(admin=user)
            )
            .distinct()
        )

    def applications_for_evaluator(self, user):
        if user.is_staff or self.evaluators.filter(id=user.id).exists() or user.id == self.admin_id:
            return self.applications.all()
        if user.organization in self.submitted_organizations.all():
            return self.applications.filter(
                scores__evaluator__organizations__in=self.submitted_organizations.all()
            ).distinct()
        return self.applications.filter(evaluating_organizations__users=user).distinct()

    def clone(self):
        copy = ApplicationRound.objects.create(name=f"Copy of {self.name}")
        groupCopies = {}
        for group in self.criterion_groups.all():
            groupCopies[group.id] = copy.criterion_groups.create(
                name=group.name, threshold=group.threshold, order=group.order, abbr=group.abbr
            )
        for group in self.criterion_groups.all():
            groupCopies[group.id].parent = groupCopies.get(group.parent_id, None)
            groupCopies[group.id].save()
        for criterion in self.criteria.all():
            copy.criteria.create(
                name=criterion.name,
                group=groupCopies[criterion.group_id],
                public=criterion.public,
                order=criterion.order,
                weight=criterion.weight,
            )

    def organization_scores_completed(self, organization):
        applications = self.applications.filter(evaluating_organizations=organization).count()
        scored = self.applications.filter(scores__evaluator__organizations=organization).distinct().count()

        return scored >= applications

    def scores_for_organization(self, organization):
        return self.scores().filter(evaluator__organizations=organization)

    def scores(self):
        return Score.objects.filter(application__application_round=self)

    def submit_by_user(self, user):
        if self.organization_scores_completed(user.organization):
            return self.submittals.create(user=user, organization=user.organization)
        else:
            raise ValueError("Scores not completed, submittal not allowed.")

    def organization_has_submitted(self, organization):
        if not organization:
            return False
        return organization.id in [o.id for o in self.submitted_organizations.all()]


def upload_round_attachment_to(instance, filename):
    return f"application_round_attachments/{secrets.token_hex(32)}/{filename}"


class ApplicationRoundAttachment(NamedModel):
    application_round = models.ForeignKey(ApplicationRound, related_name="attachments", on_delete=models.CASCADE)
    attachment = models.FileField(upload_to=upload_round_attachment_to, max_length=256)


class CriterionGroup(NamedModel):
    """
    Grouping element for the evaluation criteria. Can be used to create a hierarchy of any depth.
    """

    abbr = models.CharField(max_length=8, blank=True)
    application_round = models.ForeignKey(ApplicationRound, related_name="criterion_groups", on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "CriterionGroup", related_name="child_groups", on_delete=models.CASCADE, null=True, blank=True
    )
    order = models.IntegerField(default=0)
    threshold = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ["application_round_id", "order"]


class Criterion(NamedModel):
    """
    Criterion by which the applications are evaluated.
    """

    application_round = models.ForeignKey(ApplicationRound, related_name="criteria", on_delete=models.CASCADE)
    group = models.ForeignKey(CriterionGroup, related_name="criteria", on_delete=models.CASCADE, null=True, blank=True)
    public = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    weight = models.FloatField(default=0)

    class Meta:
        ordering = ["group_id", "order"]


class Organization(NamedModel):
    users = models.ManyToManyField(User, blank=True, related_name="organizations")


def organization(user):
    if not hasattr(user, "_organization"):
        orgs = list(user.organizations.all())
        user._organization = orgs[0] if len(orgs) else None
    return user._organization


User.organization = property(organization)


class Application(NamedModel):
    application_round = models.ForeignKey(ApplicationRound, related_name="applications", on_delete=models.CASCADE)
    application_id = models.CharField(max_length=64, blank=True)  # Application ID (18 char) from Salesforce CSV
    other_id = models.CharField(max_length=128, blank=True)  # id generated by some other system
    evaluating_organizations = models.ManyToManyField(Organization, related_name="applications_to_evaluate", blank=True)
    description = description_field()
    approved_by = models.ForeignKey(
        User, related_name="approved_applications", on_delete=models.SET_NULL, null=True, blank=True
    )
    approved = models.BooleanField(default=False)
    visibility = models.IntegerField(default=1)  # 0 = not shown, 1 = visible

    def score(self):
        # Use .all() to force evaluation of the queryset for later:
        if not len(self.scores.all()):
            return 0
        total = 0

        mean = lambda scores: sum(scores) / len(scores) if len(scores) else 0  # noqa

        for criterion in self.application_round.criteria.all():
            scores = [s for s in self.scores.all() if s.criterion_id == criterion.id]
            if len(scores):
                if self.application_round.scoring_model == "Organizations average":
                    orgs = {s.evaluator.organization.id for s in scores if s.evaluator.organization}
                    org_scores = [
                        mean([s.score for s in scores if s.evaluator.organization.id == org_id]) for org_id in orgs
                    ]
                    total += mean(org_scores) * criterion.weight
                else:
                    total += mean([s.score for s in scores]) * criterion.weight
        return total / self.application_round.total_weight()

    def all_scores(self):
        # Use .all() to force evaluation of the queryset for later:
        if not len(self.scores.all()):
            return 0

        mean = lambda scores: sum(scores) / len(scores) if len(scores) else 0  # noqa
        criterion_scores = []
        for criterion in self.application_round.criteria.all():
            scores = [s for s in self.scores.all() if s.criterion_id == criterion.id]
            if len(scores):
                if self.application_round.scoring_model == "Organizations average":
                    raise ValueError("'Organizations average' is not implemented")
                else:
                    s = mean([s.score for s in scores])  # * criterion.weight / self.application_round.total_weight()
                    # print(scores)
                    # print(s)
                    # print(criterion.weight, self.application_round.total_weight())
                    # exit()
                    criterion_scores.append((criterion.name, s))
                    print(f"{criterion.name}: {s}")
        return criterion_scores

    def can_be_evaluated_by(self, user):
        return (
            self.evaluating_organizations.filter(users=user).exists()
            or self.application_round.evaluators.filter(id=user.id).exists()
        )

    def scores_for_evaluator(self, user):
        return Score.filter_for_evaluator(self.scores.all(), user, self.application_round)

    def comments_for_evaluator(self, user):
        return Comment.filter_for_evaluator(self.comments.all(), user, self.application_round)

    @classmethod
    def applications_for_evaluator(cls, user):
        if user.is_staff:
            return cls.objects.all()
        return cls.objects.filter(
            models.Q(evaluating_organizations__users=user)
            | models.Q(application_round__evaluators=user)
            | models.Q(application_round__admin=user)
        ).distinct()

    def approve_by_user(self, user):
        self.approved_by = user
        self.approved = True
        self.save()

    def unapprove(self):
        self.approved_by = None
        self.approved = False
        self.save()


def upload_attachment_to(instance, filename):
    return f"application_attachments/{secrets.token_hex(32)}/{filename}"


class ApplicationAttachment(NamedModel):
    application = models.ForeignKey(Application, related_name="attachments", on_delete=models.CASCADE)
    attachment = models.FileField(upload_to=upload_attachment_to, max_length=256)

    def save(self, **kwargs):
        if self.attachment and not self.name:
            self.name = self.attachment.name
        return super().save(**kwargs)


class EvaluationModel(TimestampedModel):
    """
    Model used for evaluating applications
    """

    application = models.ForeignKey(Application, related_name="%(class)ss", on_delete=models.CASCADE)
    evaluator = models.ForeignKey(User, related_name="%(class)ss", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    @staticmethod
    def filter_for_evaluator(instances, user, application_round):
        """
        Returns a list of instances (scores / comments) that the user is allowed to see.
        """
        if not user:
            return []
        if user.is_staff or application_round.scoring_completed or user.id == application_round.admin_id:
            return instances
        if not user.organization:
            return [s for s in instances if s.evaluator_id == user.id]

        submitted_organizations = application_round.submitted_organizations.all()
        submitted = user.organization in submitted_organizations
        if submitted:
            return [
                s for s in instances if s.evaluator.organization and s.evaluator.organization in submitted_organizations
            ]
        return [s for s in instances if s.evaluator.organization and s.evaluator.organization == user.organization]


class Score(EvaluationModel):
    score = models.FloatField(default=0)
    criterion = models.ForeignKey(Criterion, related_name="scores", on_delete=models.CASCADE)

    def __str__(self):
        return f"Score(score={self.score}, application={self.application_id}, criterion={self.criterion_id})"


class Comment(EvaluationModel):
    comment = models.TextField(blank=True)
    criterion_group = models.ForeignKey(CriterionGroup, related_name="comments", on_delete=models.CASCADE)


class ApplicationRoundSubmittal(Model):
    application_round = models.ForeignKey(ApplicationRound, related_name="submittals", on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, related_name="submittals", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="submittals", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class BaseApplicationImport(Model):
    application_round = models.ForeignKey(ApplicationRound, related_name="%(class)ss", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="application_imports", max_length=256)
    error = models.TextField(blank=True)
    status = models.CharField(
        max_length=16,
        choices=(
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("error", "Error"),
            ("done", "Done"),
        ),
        default="pending",
    )

    class Meta:
        abstract = True

    def save(self, **kwargs):
        if self.file and (self.status == "pending"):
            self.status = "processing"
            super().save(**kwargs)
            try:
                self._process()
            except Exception as e:
                self.error = str(e)
                self.status = "error"
            else:
                self.status = "done"
        return super().save()


class ApplicationImport(BaseApplicationImport):
    application_round = models.ForeignKey(
        ApplicationRound, related_name="%(class)ss", on_delete=models.SET_NULL, null=True, blank=True
    )
    application_name_column = "Application Number"
    application_round_column = "Open Call Name"

    ignore_columns = ["Applications"]

    def _open_file(self):
        if self.file.storage.__class__.__name__ == "InMemoryStorage":
            return self.file.open("r")
        else:
            return open(self.file.path, "r", encoding="utf-8-sig")

    def _process(self):
        # Replace two spaces with \n\n, Salesforce CSV export does the opposite:
        fix_newlines = lambda s: s.replace("  ", "\n\n")  # noqa

        with self._open_file() as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.pop(self.application_name_column)
                application_id = row.pop("Application ID (18 char)")
                for column in self.ignore_columns:
                    row.pop(column, None)
                if self.application_round:
                    app_round = self.application_round
                else:
                    app_round_name = row.pop(self.application_round_column)
                    app_round = ApplicationRound.objects.get_or_create(name=app_round_name)[0]
                description = "\n\n".join([f"#### {k}\n\n{fix_newlines(v)}" for k, v in row.items()])
                _ = Application.objects.create(
                    application_round=app_round,
                    application_id=application_id,
                    name=name,
                    description=description,
                )


class ApplicationAttachmentImport(BaseApplicationImport):
    def _process(self):
        # Open the zip in self.file and loop through contents:
        with zipfile.ZipFile(self.file) as zip:
            for info in zip.infolist():
                name = info.filename.split("/")[-1].split(".")[0]
                if info.is_dir() or not name:
                    continue
                try:
                    _ = self.application_round.applications.get(name=name)
                except Application.DoesNotExist:
                    raise ValueError(f"Application {name} not found")
                with zip.open(info.filename) as f:
                    attachment = ApplicationAttachment.objects.create(
                        application=self.application_round.applications.get(name=name),
                        attachment=File(f),
                    )
                    attachment.save()
