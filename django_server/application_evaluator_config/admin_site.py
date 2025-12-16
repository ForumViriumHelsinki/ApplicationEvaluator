from django.contrib import admin


class AdminSite(admin.AdminSite):
    site_header = "FVH Application Evaluator Admin"
    site_title = "FVH Application Evaluator Admin"
    site_url = None
