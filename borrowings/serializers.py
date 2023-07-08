from django.utils import timezone
from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from borrowings.tasks import send_telegram_notification
from payment.serializers import PaymentSerializer
from payment.utils import create_stripe_session


class BorrowListSerializer(serializers.ModelSerializer):
    inventory = serializers.IntegerField(source="book.inventory", read_only=True)
    book = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.filter(inventory__gt=0)
    )

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "inventory",
            "book",
            "user",
        ]
        read_only_fields = ["actual_return_date", "user"]

    def validate(self, attrs):
        if attrs.get("expected_return_date") < timezone.localtime(timezone.now()):
            raise serializers.ValidationError(
                "Expected return date cannot be in the past."
            )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(user=user, **validated_data)

        create_stripe_session(borrowing, request)
        send_telegram_notification.delay(borrowing.id)

        return borrowing


class BorrowDetailSerializer(BorrowListSerializer):
    book = BookSerializer(many=False, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        ]
        read_only_fields = ["actual_return_date", "user", "book", "payments"]
