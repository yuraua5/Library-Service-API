from django.urls import path, include
from rest_framework import routers
from payment.views import PaymentViewSet, PaymentSuccessView, PaymentCancelView

router = routers.DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("payment/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("payment/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
] + router.urls

app_name = "payment"
