# Generated by Django 3.1.5 on 2021-01-26 15:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('application_evaluator', '0003_criterion_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='criteriongroup',
            name='threshold',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
