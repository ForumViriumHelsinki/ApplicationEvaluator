from django.contrib.admin.apps import AdminConfig


class AdminConfig(AdminConfig):
    default_site = "application_evaluator_config.admin_site.AdminSite"
