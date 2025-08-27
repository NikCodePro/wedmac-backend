from django.db import models
from users.models import User

class Document(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('pdf', 'PDF'),
        ('doc', 'DOC'),
        ('aadhar', 'Aadhar Card'),
        ('pan', 'PAN Card'),
        ('dl', 'Driving License'),
        ('other', 'Other'),
    ]

    # Optional: store raw file if needed (not used with Cloudinary)
    file_data = models.BinaryField(null=True, blank=True)

    # File name
    file_name = models.CharField(max_length=255, default='default_name')

    # Cloudinary file URL
    file_url = models.URLField(max_length=1000, null=True, blank=True)

    # Cloudinary public_id for deletion
    public_id = models.CharField(max_length=255, null=True, blank=True)

    # Type/category of the file
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='image')

    # Who uploaded it
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # Tag to describe the purpose (e.g. 'front', 'signed')
    tag = models.CharField(max_length=50, blank=True)

    # Only one active doc per user per file_type
    is_active = models.BooleanField(default=True)

    # Upload timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} ({self.tag})"
