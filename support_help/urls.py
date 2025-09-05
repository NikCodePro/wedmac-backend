from django.urls import path
from . import views

app_name = 'support_help'

urlpatterns = [
    # Artist endpoints
    path('artist/tickets/', views.ArtistTicketListView.as_view(), name='artist-ticket-list'),
    path('artist/tickets/create/', views.ArtistTicketCreateView.as_view(), name='artist-ticket-create'),
    path('artist/tickets/<int:pk>/', views.ArtistTicketDetailView.as_view(), name='artist-ticket-detail'),
    path('artist/tickets/summary/', views.artist_tickets_summary, name='artist-tickets-summary'),
    
    # Admin endpoints
    path('admin/tickets/', views.AdminTicketListView.as_view(), name='admin-ticket-list'),
    path('admin/tickets/<int:pk>/', views.AdminTicketUpdateView.as_view(), name='admin-ticket-update'),
    path('admin/tickets/<int:pk>/delete/', views.AdminTicketDeleteView.as_view(), name='admin-ticket-delete'),
    path('admin/dashboard/', views.AdminDashboardStatsView.as_view(), name='admin-dashboard-view'),
]