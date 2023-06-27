from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from Library_Service_API.permissions import IsOwnerOrAdmin
from payment.models import Payment
from payment.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
