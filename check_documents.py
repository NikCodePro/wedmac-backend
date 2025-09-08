import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wedmac_services.settings')
django.setup()

from leads.models.false_lead_claim import FalseLeadClaim
from documents.models import Document

print("False Claim Documents:")
claims = FalseLeadClaim.objects.all()
for claim in claims:
    docs = claim.proof_documents.filter(is_active=True)  # Only active docs
    if docs:
        print(f"Claim {claim.id}: {[d.file_name for d in docs]}")
    else:
        print(f"Claim {claim.id}: No active documents")

print("\nAll Documents:")
docs = Document.objects.all()
for doc in docs:
    print(f"Doc {doc.id}: {doc.file_name} - tag: {doc.tag} - active: {doc.is_active}")
