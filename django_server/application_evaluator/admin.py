from django.contrib import admin
from application_evaluator import models


class CriterionGroupInline(admin.TabularInline):
    model = models.CriterionGroup
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('order', 'name')


class CriterionInline(admin.TabularInline):
    model = models.Criterion
    extra = 0


@admin.register(models.ApplicationRound)
class ApplicationRoundAdmin(admin.ModelAdmin):
    inlines = [CriterionGroupInline, CriterionInline]


class ScoreInline(admin.TabularInline):
    model = models.Score
    extra = 0


@admin.register(models.Application)
class ApplicationAdmin(admin.ModelAdmin):
    inlines = [ScoreInline]
    list_display = ['name', 'score']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('scores', 'application_round__criteria')


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


admin.site.register(models.Organization)
