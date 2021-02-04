from django.contrib import admin
from django import forms
from django.db.models import Count

from application_evaluator import models


class InlineForApplicationRound(admin.TabularInline):
    extra = 0
    filter_fks = []

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name in self.filter_fks:
            if request._obj_ is not None:
                field.queryset = field.queryset.filter(application_round=request._obj_)
            else:
                field.queryset = field.queryset.none()
        return field


class CriterionGroupInline(InlineForApplicationRound):
    model = models.CriterionGroup
    filter_fks = ['parent']

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', 'name')


class CriterionInline(InlineForApplicationRound):
    model = models.Criterion
    filter_fks = ['group']


class ApplicationInline(admin.TabularInline):
    model = models.Application
    extra = 0


class ApplicationRoundForm(forms.ModelForm):
    import_applications = forms.CharField(
        widget=forms.Textarea({'rows': 3}),
        required=False,
        help_text='Paste application names here, one per row; optionally, you can also ' +
                  'include evaluating organizations after application name, separated by tabs.')

    class Meta:
        model = models.ApplicationRound
        exclude = []

    def save(self, commit=True):
        round = super().save(commit)
        if commit:
            self.save_applications()
        return round

    def _save_m2m(self):
        self.save_applications()
        return super()._save_m2m()

    def save_applications(self):
        orgs = dict((o.name, o) for o in models.Organization.objects.all())
        for row in self.data['import_applications'].strip().split('\n'):
            parts = row.strip().split('\t')
            name = parts.pop(0)
            if not name:
                continue
            app = self.instance.applications.create(name=name)
            for org_name in parts:
                org = orgs.get(org_name.strip(), None)
                if org:
                    app.evaluating_organizations.add(org)


@admin.register(models.ApplicationRound)
class ApplicationRoundAdmin(admin.ModelAdmin):
    inlines = [CriterionGroupInline, CriterionInline, ApplicationInline]
    list_display = ['name', 'applications_']
    actions = ['duplicate']
    form = ApplicationRoundForm

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(app_count=Count('applications'))

    def applications_(self, round):
        return round.app_count

    def duplicate(self, request, queryset):
        for round in queryset:
            round.clone()

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)


class ScoreInline(admin.TabularInline):
    model = models.Score
    extra = 0


def add_evaluating_organization_action(organization):
    def action(modeladmin, request, queryset):
        for app in queryset.all():
            app.evaluating_organizations.add(organization)

    action.__name__ = f'Allocate to {organization.name}'
    return action


@admin.register(models.Application)
class ApplicationAdmin(admin.ModelAdmin):
    inlines = [ScoreInline]
    list_display = ['name', 'organizations', 'score', 'scores_']
    list_filter = ['application_round', 'evaluating_organizations']

    def get_actions(self, request):
        self.actions = [add_evaluating_organization_action(o)
                        for o in models.Organization.objects.order_by('name')]
        return super().get_actions(request)

    def scores_(self, app):
        return len(app.scores.all())

    def organizations(self, app):
        return ', '.join(o.name for o in app.evaluating_organizations.all())

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .prefetch_related('scores', 'application_round__criteria', 'evaluating_organizations')


class CriterionScoreInline(ScoreInline):
    readonly_fields = ['evaluator', 'application']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('application', 'evaluator')


@admin.register(models.Criterion)
class CriterionAdmin(admin.ModelAdmin):
    inlines = [CriterionScoreInline]
    actions = ['initialize_scores', 'delete_my_scores']

    def initialize_scores(self, request, queryset):
        for criterion in queryset:
            for app in criterion.application_round.applications.exclude(scores__criterion=criterion).order_by('name'):
                app.scores.create(criterion=criterion, evaluator=request.user)

    def delete_my_scores(self, request, queryset):
        models.Score.objects.filter(evaluator=request.user, criterion__in=queryset).delete()


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    filter_horizontal = ['users']
