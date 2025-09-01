# Generated manually to fix total_bookings default value issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0013_lead_total_claims'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lead',
            name='total_bookings',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='lead',
            name='total_claims',
            field=models.IntegerField(default=0),
        ),
    ]
