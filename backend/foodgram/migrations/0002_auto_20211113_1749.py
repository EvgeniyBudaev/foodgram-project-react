# Generated by Django 3.2.9 on 2021-11-13 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ingredient',
            name='unique_ingredient',
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name',), name='unique_ingredient'),
        ),
    ]
