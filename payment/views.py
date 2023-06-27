from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Library_Service_API.permissions import IsOwnerOrAdmin
from payment.models import Payment
from payment.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


class PaymentSuccessView(generics.GenericAPIView):
    serializer_class = PaymentSerializer

    def get(self, request):
        session_id = request.GET.get("session_id")
        if session_id:
            payment = Payment.objects.filter(session_id=session_id).first()
            if payment:
                payment.status = Payment.StatusChoices.PAID
                payment.save()
                return Response({"message": "Payment successful."})
        return Response({"message": "Payment not found."}, status=status.HTTP_400_BAD_REQUEST)


class PaymentCancelView(APIView):
    def get(self, request):
        return Response({'message': 'Payment can be made later. The session is available for 24 hours.'})
