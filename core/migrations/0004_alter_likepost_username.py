# Generated by Django 5.0.7 on 2024-08-12 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_likepost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='likepost',
            name='username',
            field=models.CharField(max_length=100),
        ),
    ]
