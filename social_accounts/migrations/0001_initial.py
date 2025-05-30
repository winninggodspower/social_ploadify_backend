# Generated by Django 5.2 on 2025-05-28 12:01

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('is_default', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brands', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SocialAccount',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account_type', models.CharField(choices=[('youtube', 'YouTube'), ('instagram', 'Instagram'), ('tiktok', 'TikTok'), ('facebook', 'Facebook')], max_length=50)),
                ('_access_token', models.TextField()),
                ('_refresh_token', models.TextField(blank=True, null=True)),
                ('expires_at', models.DateTimeField()),
                ('scope', models.TextField(blank=True, null=True)),
                ('token_type', models.CharField(default='Bearer', max_length=50)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_accounts', to='social_accounts.brand')),
            ],
        ),
        migrations.AddConstraint(
            model_name='brand',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='unique_user_brand_name'),
        ),
        migrations.AddConstraint(
            model_name='brand',
            constraint=models.UniqueConstraint(fields=('user', 'is_default'), name='unique_user_default_brand'),
        ),
        migrations.AddConstraint(
            model_name='socialaccount',
            constraint=models.UniqueConstraint(fields=('brand', 'account_type'), name='unique_brand_social_account'),
        ),
    ]
