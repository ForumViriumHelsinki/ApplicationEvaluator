# Generated by Django 3.1.5 on 2023-03-16 10:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('application_evaluator', '0017_applicationimport'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='application',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='approved_applications', to=settings.AUTH_USER_MODEL),
        ),
    ]
