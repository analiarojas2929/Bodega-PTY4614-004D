# Generated by Django 5.1 on 2024-11-06 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Polls', '0011_alter_customuser_roles_alter_role_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='roles',
            field=models.ManyToManyField(related_name='users', to='Polls.role'),
        ),
    ]