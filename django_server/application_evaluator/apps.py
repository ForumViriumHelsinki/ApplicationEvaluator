from django.contrib.admin.apps import AdminConfig


class AdminConfig(AdminConfig):
    default_site = 'application_evaluator.admin_site.AdminSite'
