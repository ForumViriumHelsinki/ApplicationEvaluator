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


admin.site.register(models.Organization)
