# Generated by Django 3.0.7 on 2021-03-03 08:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_auto_20210217_0601'),
        ('transactions', '0003_auto_20210302_1230'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='everydaysale',
            unique_together={('date', 'super_market', 'supplier_name')},
        ),
    ]
