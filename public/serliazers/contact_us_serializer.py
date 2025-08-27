from rest_framework import serializers

from public.models import ContactUs


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id', 'name', 'mobile', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']
