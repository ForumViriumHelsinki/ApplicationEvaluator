from django.contrib.auth.models import User
from rest_framework import serializers, routers, viewsets, permissions

from application_evaluator import models


class CriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Criterion
        fields = ['name', 'group', 'id']


class CriterionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CriterionGroup
        fields = ['name', 'parent', 'id']


class EvaluatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username']


class BaseScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Score
        fields = ['score', 'evaluator', 'criterion', 'application', 'id']


class ScoreSerializer(BaseScoreSerializer):
    evaluator = EvaluatorSerializer(read_only=True)


class ApplicationSerializer(serializers.ModelSerializer):
    scores = serializers.SerializerMethodField()

    class Meta:
        model = models.Application
        fields = ['name', 'scores', 'id']

    def get_scores(self, application):
        return ScoreSerializer(
            application.scores_for_evaluator(self.context['request'].user).select_related('evaluator'),
            many=True
        ).data


class ApplicationRoundSerializer(serializers.ModelSerializer):
    applications = serializers.SerializerMethodField()
    criteria = CriterionSerializer(many=True, read_only=True)
    criterion_groups = CriterionGroupSerializer(many=True, read_only=True)

    class Meta:
        model = models.ApplicationRound
        fields = '__all__'

    def get_applications(self, application_round):
        return ApplicationSerializer(
            application_round.applications_for_evaluator(self.context['request'].user).order_by('name'),
            many=True, context=self.context
        ).data


class ApplicationRoundViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApplicationRoundSerializer

    def get_queryset(self):
        return models.ApplicationRound.rounds_for_evaluator(self.request.user) \
            .prefetch_related('criteria', 'criterion_groups')


class ScoreViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BaseScoreSerializer

    def get_queryset(self):
        return models.Score.objects.filter(evaluator=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data['evaluator'] = request.user.id
        return super().create(request, *args, **kwargs)


class ApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return models.Application.applications_for_evaluator(self.request.user)


router = routers.DefaultRouter()
router.register('application_rounds', ApplicationRoundViewSet, 'application_round')
router.register('scores', ScoreViewSet, 'score')
router.register('applications', ApplicationViewSet, 'application')
