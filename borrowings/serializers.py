from django.utils import timezone
from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing


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


class BorrowDetailSerializer(BorrowListSerializer):
    book = BookSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]
        read_only_fields = ["actual_return_date", "user", "book"]
