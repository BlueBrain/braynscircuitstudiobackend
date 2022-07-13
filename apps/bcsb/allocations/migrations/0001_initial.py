# Generated by Django 3.2.9 on 2022-07-13 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bcsb_sessions', '0001_initial'),
        ('unicore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hostname', models.CharField(max_length=50)),
                ('port', models.PositiveSmallIntegerField()),
                ('status', models.CharField(max_length=20)),
                ('script', models.TextField(blank=True)),
                ('stdout', models.TextField(blank=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bcsb_sessions.session')),
                ('unicore_job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicore.unicorejob')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
