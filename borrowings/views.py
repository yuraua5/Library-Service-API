from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from Library_Service_API.permissions import IsOwnerOrAdmin
from books.pagination import Pagination
from borrowings.models import Borrowing

from borrowings.serializers import BorrowListSerializer, BorrowDetailSerializer
from payment.utils import create_stripe_session




class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related("book")
    serializer_class = BorrowListSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    pagination_class = Pagination

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if is_active:
            if is_active == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            if is_active == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)
        return queryset

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
        create_stripe_session(borrowing, self.request)

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"message": "Book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.actual_return_date = timezone.now()
        borrowing.save()
        book = borrowing.book
        book.inventory += 1
        book.save()

        return Response({"message": "Book returned successfully."})

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user_id",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by user id (ex. ?user_id=1)",
            ),
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.STR,
                description="Filter by is active (ex. ?is_active=true)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
