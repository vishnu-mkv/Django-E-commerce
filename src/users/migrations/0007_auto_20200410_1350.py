# Generated by Django 3.0.4 on 2020-04-10 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_user_mail_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailactivation',
            name='mail_sent',
            field=models.BooleanField(default=True),
        ),
    ]