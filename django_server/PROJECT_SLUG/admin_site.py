from django.contrib import admin


class AdminSite(admin.AdminSite):
    site_header = '$PROJECT_NAME Admin'
    site_title = '$PROJECT_NAME Admin'
    site_url = None
