# Generated by Django 5.0.9 on 2024-09-17 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('title', models.CharField(max_length=500)),
                ('comments', models.TextField()),
                ('date', models.DateField(auto_now_add=True)),
            ],
        ),
    ]
