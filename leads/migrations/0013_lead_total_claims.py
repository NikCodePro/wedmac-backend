# Generated manually to add total_bookings and total_claims fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0011_lead_booked_artists_lead_claimed_artists_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='total_bookings',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='lead',
            name='total_claims',
            field=models.IntegerField(default=0),
        ),
    ]
