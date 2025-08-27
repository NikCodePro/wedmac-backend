from django.urls import path
from .views import MasterDataListAPIView

urlpatterns = [
    path('list/', MasterDataListAPIView.as_view(), name='master-data-list'),
]
