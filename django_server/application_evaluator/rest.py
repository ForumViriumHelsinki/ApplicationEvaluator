from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import serializers, routers, viewsets, permissions

from application_evaluator import models


class CriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Criterion
        fields = ['name', 'group', 'id', 'weight']


class CriterionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CriterionGroup
        fields = ['name', 'abbr', 'parent', 'id', 'threshold']


class UserSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'organization']

    def get_organization(self, user):
        return user.organization.name if user.organization else None


class BaseScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Score
        fields = ['score', 'evaluator', 'criterion', 'application', 'id']


class ScoreSerializer(BaseScoreSerializer):
    evaluator = UserSerializer(read_only=True)


class ApplicationSerializer(serializers.ModelSerializer):
    scores = serializers.SerializerMethodField()
    evaluating_organizations = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)

    class Meta:
        model = models.Application
        fields = ['name', 'scores', 'id', 'evaluating_organizations']

    def get_scores(self, application):
        return ScoreSerializer(
            application.scores_for_evaluator(self.context['request'].user),
            many=True
        ).data


class ApplicationRoundSerializer(serializers.ModelSerializer):
    applications = serializers.SerializerMethodField()
    criteria = serializers.SerializerMethodField()
    criterion_groups = CriterionGroupSerializer(many=True, read_only=True)

    class Meta:
        model = models.ApplicationRound
        fields = '__all__'

    def get_applications(self, application_round):
        user = self.context['request'].user
        applications = application_round \
            .applications_for_evaluator(user) \
            .prefetch_related('evaluating_organizations', 'scores__evaluator__organizations') \
            .order_by('name')
        return ApplicationSerializer(applications, many=True, context=self.context).data

    def get_criteria(self, application_round):
        criteria = application_round.criteria.all()
        if not self.context['request'].user.is_staff:
            criteria = criteria.filter(public=True)
        return CriterionSerializer(criteria, many=True, context=self.context).data


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ApplicationRoundViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApplicationRoundSerializer

    def get_queryset(self):
        return models.ApplicationRound.rounds_for_evaluator(self.request.user) \
            .prefetch_related('criterion_groups')


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
