from django.contrib.auth.models import User
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import serializers, routers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from application_evaluator import models


class ModelSerializer(serializers.ModelSerializer):
    def user(self):
        return self.context['request'].user


class CriterionSerializer(ModelSerializer):
    class Meta:
        model = models.Criterion
        fields = ['name', 'group', 'id', 'weight']


class CriterionGroupSerializer(ModelSerializer):
    class Meta:
        model = models.CriterionGroup
        fields = ['name', 'abbr', 'parent', 'id', 'threshold']


class UserSerializer(ModelSerializer):
    organization = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'organization']

    def get_organization(self, user):
        return user.organization.name if user.organization else None


class BaseScoreSerializer(ModelSerializer):
    class Meta:
        model = models.Score
        fields = ['score', 'evaluator', 'criterion', 'application', 'id']


class ScoreSerializer(BaseScoreSerializer):
    evaluator = UserSerializer(read_only=True)


class BaseCommentSerializer(ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ['comment', 'evaluator', 'criterion_group', 'application', 'id', 'created_at']


class CommentSerializer(BaseCommentSerializer):
    evaluator = UserSerializer(read_only=True)


class AttachmentSerializer(ModelSerializer):
    class Meta:
        model = models.ApplicationAttachment
        fields = ['name', 'attachment']


class ApplicationSerializer(ModelSerializer):
    scores = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    evaluating_organizations = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    prefetch_related = [
        'evaluating_organizations',
        'scores__evaluator__organizations',
        'comments__evaluator__organizations',
        'attachments']

    class Meta:
        model = models.Application
        fields = ['name', 'description', 'scores', 'comments', 'id', 'evaluating_organizations', 'attachments']

    def get_scores(self, application):
        return ScoreSerializer(application.scores_for_evaluator(self.user()), many=True).data

    def get_comments(self, application):
        return CommentSerializer(application.comments_for_evaluator(self.user()), many=True).data


class ApplicationRoundAttachmentSerializer(ModelSerializer):
    class Meta:
        model = models.ApplicationRoundAttachment
        fields = ['name', 'attachment']


class ApplicationRoundSerializer(ModelSerializer):
    applications = serializers.SerializerMethodField()
    criteria = serializers.SerializerMethodField()
    criterion_groups = CriterionGroupSerializer(many=True, read_only=True)
    attachments = ApplicationRoundAttachmentSerializer(many=True, read_only=True)
    submitted_organizations = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)

    class Meta:
        model = models.ApplicationRound
        exclude = ['published']

    def get_applications(self, application_round):
        user = self.user()
        applications = application_round \
            .applications_for_evaluator(user) \
            .prefetch_related(*ApplicationSerializer.prefetch_related) \
            .order_by('name')
        return ApplicationSerializer(applications, many=True, context=self.context).data

    def get_criteria(self, application_round):
        criteria = application_round.criteria.all()
        if not (self.user().is_staff or
                application_round.organization_has_submitted(self.user().organization)):
            criteria = criteria.filter(public=True)
        return CriterionSerializer(criteria, many=True, context=self.context).data


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ApplicationRoundViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApplicationRoundSerializer

    def get_queryset(self):
        return models.ApplicationRound.rounds_for_evaluator(self.request.user) \
            .prefetch_related('criterion_groups', 'attachments', 'submitted_organizations')

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        instance = get_object_or_404(models.ApplicationRound.rounds_for_evaluator(self.request.user), id=pk)
        try:
            instance.submit_by_user(request.user)
        except ValueError:
            raise Http404
        return self.retrieve(request, pk=pk)


class EvaluationModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(evaluator=self.request.user) \
            .exclude(application__application_round__submitted_organizations=self.request.user.organization)

    def create(self, request, *args, **kwargs):
        get_object_or_404(
            models.Application.objects.exclude(
                application_round__submitted_organizations=self.request.user.organization),
            id=request.data['application'])
        request.data['evaluator'] = request.user.id
        return super().create(request, *args, **kwargs)


class ScoreViewSet(EvaluationModelViewSet):
    serializer_class = BaseScoreSerializer
    queryset = models.Score.objects.all()


class CommentViewSet(EvaluationModelViewSet):
    serializer_class = BaseCommentSerializer
    queryset = models.Comment.objects.all()


class ApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return models.Application.applications_for_evaluator(self.request.user) \
            .prefetch_related(*ApplicationSerializer.prefetch_related)


router = routers.DefaultRouter()
router.register('application_rounds', ApplicationRoundViewSet, 'application_round')
router.register('scores', ScoreViewSet, 'score')
router.register('comments', CommentViewSet, 'comment')
router.register('applications', ApplicationViewSet, 'application')
