from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_testattempt'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=50)),
                ('title', models.CharField(max_length=255)),
                ('occurred_at', models.DateTimeField()),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-occurred_at', '-id'),
            },
        ),
        migrations.CreateModel(
            name='CompanyTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('readiness_percentage', models.PositiveSmallIntegerField(default=0)),
                ('focus', models.CharField(blank=True, max_length=180)),
                ('tone', models.CharField(choices=[('green', 'Green'), ('amber', 'Amber'), ('red', 'Red'), ('slate', 'Slate')], default='slate', max_length=20)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_targets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('order', 'name'),
            },
        ),
        migrations.CreateModel(
            name='DailyPlanItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=180)),
                ('detail', models.CharField(blank=True, max_length=255)),
                ('status', models.CharField(blank=True, max_length=80)),
                ('progress_percentage', models.PositiveSmallIntegerField(default=0)),
                ('tone', models.CharField(choices=[('cyan', 'Cyan'), ('green', 'Green'), ('amber', 'Amber'), ('red', 'Red'), ('violet', 'Violet'), ('slate', 'Slate')], default='cyan', max_length=20)),
                ('date', models.DateField()),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('is_completed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_plan_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('date', 'order', 'id'),
            },
        ),
        migrations.CreateModel(
            name='InterviewReadiness',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area', models.CharField(max_length=80)),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('max_score', models.PositiveSmallIntegerField(default=10)),
                ('progress_percentage', models.PositiveSmallIntegerField(default=0)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interview_readiness_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('order', 'area'),
            },
        ),
        migrations.CreateModel(
            name='RevisionQueueItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=180)),
                ('cycle_label', models.CharField(max_length=50)),
                ('duration_minutes', models.PositiveSmallIntegerField(default=10)),
                ('due_date', models.DateField()),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('is_completed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revision_queue_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('due_date', 'order', 'id'),
            },
        ),
    ]
