"""application_evaluator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from rest_auth.views import LogoutView
from rest_framework.schemas import get_schema_view

from application_evaluator import rest

schema_view = get_schema_view(
    title="FVH Application Evaluator API",
    description="API for interacting with the FVH Application Evaluator application",
    version="1.0.0", public=True)


def error_view(request):
    raise Exception('This is a test error to verify error reporting.')


# Allow logging out when faced with the mysterious CSRF cookie corruption problem:
class LogoutView(LogoutView):
    authentication_classes = []


urlpatterns = [
    path('admin/', admin.site.urls),
    path('rest-auth/logout/', LogoutView.as_view()),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest/error_test/', error_view, name='error-view'),
    path('rest/', include(rest.router.urls)),
    path('openapi/', schema_view, name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui')
]
