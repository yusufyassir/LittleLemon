# Generated by Django 5.1.4 on 2025-01-14 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0002_remove_category_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='menuitem',
            old_name='Category',
            new_name='category',
        ),
    ]
