from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import BorrowListSerializer, BorrowDetailSerializer


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowListSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowListSerializer

        if self.action in ["retrieve", "update"]:
            return BorrowDetailSerializer

        return BorrowListSerializer

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)
        book = borrowing.book
        book.inventory -= 1
        book.save()

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response({"message": "Book has already been returned."}, status=status.HTTP_400_BAD_REQUEST)

        borrowing.actual_return_date = timezone.now()
        borrowing.save()
        book = borrowing.book
        book.inventory += 1
        book.save()

        return Response({"message": "Book returned successfully."})
