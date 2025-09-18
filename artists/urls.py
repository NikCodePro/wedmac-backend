from django.urls import path

from artists.view.admin_approve_artist import (
    AdminDeleteArtistView  # Add this import
)
from artists.view.admin_artist_list import AdminArtistListView
from artists.view.admin_artist_tag import AdminArtistTagView, AdminArtistTagListView
from artists.view.complete_artist_profile import CompleteArtistProfileView
from artists.view.get_artist_profile import GetArtistProfileView
from artists.view.payment_history_view import ArtistPaymentHistoryView
from artists.view.subscriptions_view import  PurchaseSubscriptionView, VerifyPaymentView
from artists.view.website.artist_card_view import ArtistCardListView
from artists.view.payment_history_view import AdminArtistPaymentHistoryView
from artists.view.website.artist_detail_view import ArtistPublicDetailView
from artists.view.refferal_code_view import generate_referral_code, get_referral_code
from artists.view.artist_service_view import ArtistServiceManageView
from artists.view.update_extended_days import UpdateExtendedDaysView
from artists.view.admin_set_current_plan import AdminSetCurrentPlanView
from artists.view.admin_update_mobile import AdminUpdateMobileView

urlpatterns = [
    path('complete-profile/', CompleteArtistProfileView.as_view(), name='complete_profile'),
    path('my-profile/', GetArtistProfileView.as_view(), name='get_artist_profile'),
    path('list/',AdminArtistListView.as_view(),name='admin-artist-list'),
    # path('subscriptions/', ListMySubscriptionsView.as_view(), name='my-subscriptions'),
    # More flexible - accepts any string format
    path('plans/<str:plan_id>/purchase/', PurchaseSubscriptionView.as_view(), name='purchase-plan'),

    path('payment/verify/', VerifyPaymentView.as_view(), name='verify-payment'),

    path('payments/history/', ArtistPaymentHistoryView.as_view(), name='artist-payment-history'),
     # Admin: all artists payment history with filters
    path('admin/payments/history/', AdminArtistPaymentHistoryView.as_view(), name='admin-artist-payment-history'),
    # website urls 
    path('cards/', ArtistCardListView.as_view(), name='artist-cards'),
    path('artist/<int:id>/', ArtistPublicDetailView.as_view(), name='public-artist-detail'),

    # Referral code endpoints
    path('referral-code/generate/', generate_referral_code, name='generate-referral-code'),
    path('referral-code/', get_referral_code, name='get-referral-code'),
   # delete artist by admin
    path('admin/<int:artist_id>/delete-artist/', AdminDeleteArtistView.as_view(), name='admin-delete-artist'),
    # Artist tag management
    path('admin/<int:artist_id>/tag/', AdminArtistTagView.as_view(), name='admin-artist-tag'),
    path('admin/tags/', AdminArtistTagListView.as_view(), name='admin-artist-tags'),
    # Update extended days
    path('admin/update-extended-days/', UpdateExtendedDaysView.as_view(), name='update-extended-days'),
    # Admin set current plan
    path('admin/<int:artist_id>/set-current-plan/', AdminSetCurrentPlanView.as_view(), name='admin-set-current-plan'),
    # Admin update artist mobile number
    path('admin/<int:artist_id>/update-mobile/', AdminUpdateMobileView.as_view(), name='admin-update-mobile'),
    # path('services/', ArtistServiceManageView.as_view(), name='artist-services'),
]

