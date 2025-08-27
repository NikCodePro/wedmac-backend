from django.db import migrations
import uuid

def fix_uuid_data(apps, schema_editor):
    SubscriptionPlan = apps.get_model('adminpanel', 'SubscriptionPlan')
    db_alias = schema_editor.connection.alias
    
    # Get all subscription plans
    for plan in SubscriptionPlan.objects.using(db_alias).all():
        try:
            # Try to convert existing id to UUID
            uuid.UUID(str(plan.id))
        except (ValueError, AttributeError):
            # If conversion fails, assign new UUID
            plan.id = uuid.uuid4()
            plan.save()

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('adminpanel', '0011_fix_subscription_uuid'),  # Update this to your last migration
    ]

    operations = [
        migrations.RunPython(fix_uuid_data, reverse_func),
    ]