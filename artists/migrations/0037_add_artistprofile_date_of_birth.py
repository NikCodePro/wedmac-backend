# Generated migration to add back the date_of_birth field to ArtistProfile model

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('artists', '0036_fix_tag_data_conversion'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistprofile',
            name='date_of_birth',
            field=models.DateField(null=True, blank=True),
        ),
    ]
