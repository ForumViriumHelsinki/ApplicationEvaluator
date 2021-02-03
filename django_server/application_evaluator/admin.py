from django.contrib import admin

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


@admin.register(models.ApplicationRound)
class ApplicationRoundAdmin(admin.ModelAdmin):
    inlines = [CriterionGroupInline, CriterionInline]
    actions = ['duplicate']

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
