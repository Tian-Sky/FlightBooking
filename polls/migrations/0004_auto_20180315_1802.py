# Generated by Django 2.0.3 on 2018-03-15 22:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_auto_20180315_1758'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='choice_new',
            name='question',
        ),
        migrations.DeleteModel(
            name='Choice_new',
        ),
        migrations.DeleteModel(
            name='Question_new',
        ),
    ]
