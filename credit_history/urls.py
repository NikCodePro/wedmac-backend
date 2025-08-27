from django.urls import path
from .views import (
    ArtistCreditBalanceView,
    ArtistCreditHistoryView,
)

urlpatterns = [
    path('balance/', ArtistCreditBalanceView.as_view(), name='credit-balance'),
    path('history/', ArtistCreditHistoryView.as_view(), name='credit-history'),
    # path('summary/', CreditSummaryView.as_view(), name='credit-summary'),
]