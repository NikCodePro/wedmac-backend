from django.urls import path
from .views import CreateOrderView, VerifyPaymentView

urlpatterns = [
    path('create-order/<int:plan_id>/', CreateOrderView.as_view()),
    path('verify-payment/', VerifyPaymentView.as_view()),
]
