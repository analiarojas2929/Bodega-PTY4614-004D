# Generated by Django 5.1 on 2024-11-16 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Polls', '0003_alter_ticket_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='roles',
            field=models.ManyToManyField(blank=True, related_name='users', to='Polls.role'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='fecha_creacion',
            field=models.DateField(auto_now_add=True),
        ),
    ]
