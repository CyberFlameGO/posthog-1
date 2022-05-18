# Generated by Django 3.2.12 on 2022-05-17 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posthog", "0233_plugin_source_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="pluginsourcefile", name="error", field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="pluginsourcefile",
            name="status",
            field=models.CharField(
                null=True,
                choices=[("LOCKED", "locked"), ("TRANSPILED", "transpiled"), ("ERROR", "error")],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="pluginsourcefile", name="transpiled", field=models.TextField(blank=True, null=True),
        ),
    ]
