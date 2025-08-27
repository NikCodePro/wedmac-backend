# leads/models/false_lead_claim.py
from django.db import models
from artists.models import ArtistProfile
from leads.models.models import Lead
from users.models import User
from documents.models import Document

class FalseLeadClaim(models.Model):
    CLAIM_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='false_claims')
    artist = models.ForeignKey(ArtistProfile, on_delete=models.CASCADE, related_name='false_lead_claims')
    
    reason = models.TextField()
    
    # Linked to your Document model (image/pdf proof, etc.)
    proof_documents = models.ManyToManyField(Document, blank=True, related_name='false_lead_claims')

    status = models.CharField(max_length=10, choices=CLAIM_STATUS_CHOICES, default='pending')
    
    admin_note = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='resolved_false_claims')

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"False Claim by {self.artist} on Lead #{self.lead.id} [{self.status}]"
