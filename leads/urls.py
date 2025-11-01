from django.urls import path

from leads.views.claim_detail_view import ClaimDetailView
from leads.views.claim_lead_view import ClaimLeadView
from leads.views.book_lead_view import BookLeadView
from leads.views.get_artist_dashboard_recent_lead_view import ArtistRecentLeadsView
from leads.views.get_lead_detail_view import LeadDetailView
from leads.views.get_leads_view import GetLeadsByStatusView
from leads.views.get_all_leads_view import GetAllLeadsView
from leads.views.get_my_claimed_leads_view import GetMyClaimedLeadsView
from leads.views.get_my_false_claims_view import GetMyFalseClaimsView
from leads.views.list_false_claims_admin_view import ListFalseClaimsAdminView
from leads.views.raise_false_claim_view import RaiseFalseLeadClaimView
from leads.views.resolve_false_claim_view import ResolveFalseClaimView
from leads.views.update_leads_view import UpdateLeadView
from leads.views.views import AdminCreateLeadView, PublicLeadSubmissionView, AdminCreateMultipleLeadsView, AdminDeleteLeadView, GetMyAssignedLeadsView, AdminSetLeadVerifiedView, AdminBulkDeleteLeadsView
from leads.views.admin_leads_count_view import AdminLeadStatusCountView
from leads.views.selected_artist_view import SelectedArtistView
from leads.views.set_max_claims_view import SetMaxClaimsView
from leads.views.bulk_set_max_claims_view import BulkSetMaxClaimsView

urlpatterns = [
    path('admin/create/', AdminCreateLeadView.as_view(), name='admin-create-lead'),
    path('admin/create-multiple/', AdminCreateMultipleLeadsView.as_view(), name='admin-create-multiple-leads'),
    path('admin/delete/<int:lead_id>/', AdminDeleteLeadView.as_view(), name='admin-delete-lead'),
    path('admin/bulk-delete/', AdminBulkDeleteLeadsView.as_view(), name='admin-bulk-delete-leads'),
    path('admin/<int:lead_id>/set-verified/', AdminSetLeadVerifiedView.as_view(), name='admin-set-lead-verified'),
    path('public/submit/', PublicLeadSubmissionView.as_view(), name='public-lead-submit'),
    path('list/', GetLeadsByStatusView.as_view(), name='get-leads-by-status'),
    path('all-leads/', GetAllLeadsView.as_view(), name='get-all-leads'),
    path('<int:lead_id>/update/', UpdateLeadView.as_view(), name='update-lead'),
    path('status-count/', AdminLeadStatusCountView.as_view(), name='admin-lead-status-count'),
    path('lead-detail/<int:lead_id>/', LeadDetailView.as_view(), name='get-single-lead'),
    path('artist/recent-leads/', ArtistRecentLeadsView.as_view()),
    path('<int:lead_id>/claim/', ClaimLeadView.as_view(), name='claim-lead'),
    path('<int:lead_id>/book/', BookLeadView.as_view(), name='book-lead'),
    path('artist/my-assigned-leads/', GetMyAssignedLeadsView.as_view(), name='my-assigned-leads'),
    path('artist/my-claimed-leads/', GetMyClaimedLeadsView.as_view(), name='my-claimed-leads'),

    # False Claims
    path('false-claims/', RaiseFalseLeadClaimView.as_view(), name='raise-false-lead-claim'),
    path('false-claims/my/', GetMyFalseClaimsView.as_view(), name='my-false-claims'),
    path('false-claims/admin/', ListFalseClaimsAdminView.as_view(), name='list-false-claims-admin'),
    path('false-claims/<int:claim_id>/', ClaimDetailView.as_view(), name='false-claim-detail'),
    path('false-claims/<int:pk>/resolve/', ResolveFalseClaimView.as_view(), name='resolve-false-claim'),

    # Selected Artists Management
    path('selected-artists/', SelectedArtistView.as_view(), name='selected-artists'),

    # Admin set max claims for a lead
    path('<int:lead_id>/set-max-claims/', SetMaxClaimsView.as_view(), name='set-max-claims'),

    # Admin bulk set max claims for all leads
    path('bulk-set-max-claims/', BulkSetMaxClaimsView.as_view(), name='bulk-set-max-claims'),
]
