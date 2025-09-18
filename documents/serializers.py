import cloudinary.uploader
from rest_framework import serializers
from .models import Document


class DocumentUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = Document
        fields = ['id', 'file', 'file_name', 'file_type', 'tag', 'created_at']
        read_only_fields = ['id', 'created_at', 'file_name']


    def create(self, validated_data):
        uploaded_file = validated_data.pop('file')
        user = self.context['request'].user

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            uploaded_file,
            resource_type="auto",  # Supports image, pdf, etc.
            folder="artist_documents/"  # Optional: Cloudinary folder
        )

        # Save metadata to DB
        document = Document.objects.create(
            uploaded_by=user,
            file_name=uploaded_file.name,
            file_type=validated_data.get('file_type', 'other'),
            tag=validated_data.get('tag', ''),
            file_url=result.get("secure_url"),
            public_id=result.get("public_id"),
            is_active=True
        )
        return document
