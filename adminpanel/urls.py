from django.urls import path
from adminpanel.serializers.subscriptions_serializers import CreateSubscriptionPlanSerializer
from adminpanel.views.get_master_list import MasterDataListAPIView
from adminpanel.views.subscriptions_view import CreateSubscriptionPlanView, SubscriptionPlanListView, UpdateSubscriptionPlanView, DeleteSubscriptionPlanView
from artists.view.admin_approve_artist import AdminApproveOrRejectArtistView, AdminChangePendingStatusView, AdminRejectArtistView, AdminSetArtistActiveView, AdminSetArtistInactiveView
from artists.view.admin_artist_list import AdminArtistListView
from adminpanel.views.create_master_data import CreateMasterDataAPIView, UpdateMasterDataAPIView, DeleteMasterDataAPIView


urlpatterns = [
    path('artists/', AdminArtistListView.as_view(), name='admin-artist-list'),
    path('artist/<int:artist_id>/status-approved/',
         AdminApproveOrRejectArtistView.as_view(), name='admin_approve_artist'),
    path('artist/<int:artist_id>/status-pending/',
         AdminChangePendingStatusView.as_view(), name='admin_pending_artist'),
    path('artist/<str:artist_id>/status-reject/',
         AdminRejectArtistView.as_view(), name='admin-reject-artist'),

    # activate / deactivate artist
    path('artist/<int:artist_id>/activate/', AdminSetArtistActiveView.as_view(), name='admin-artist-activate'),
    path('artist/<int:artist_id>/deactivate/', AdminSetArtistInactiveView.as_view(), name='admin-artist-deactivate'),

    # subscription plans (create/list already present)
    path('subscription-plans/create/',
         CreateSubscriptionPlanView.as_view(), name='subscription-plans'),
    # subscription plans list
    path('subscription-plans/', SubscriptionPlanListView.as_view(), name='subscription-plans-list'),

    # update & delete
    path('subscription-plans/<str:plan_id>/update/', UpdateSubscriptionPlanView.as_view(), name='subscription-plan-update'),
    path('subscription-plans/<str:plan_id>/delete/', DeleteSubscriptionPlanView.as_view(), name='subscription-plan-delete'),

    path('master/list/', MasterDataListAPIView.as_view(), name='master-data-list'),
    path('master/create/', CreateMasterDataAPIView.as_view(),
         name='create-master-data'),
    path('master/update/', UpdateMasterDataAPIView.as_view(),
         name='update-master-data'),
    path('master/delete/', DeleteMasterDataAPIView.as_view(),
         name='delete-master-data'),

]
