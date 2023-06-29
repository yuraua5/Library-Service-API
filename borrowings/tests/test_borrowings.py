from datetime import date, datetime

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowListSerializer

BORROWING_URL = reverse("borrowings:borrowing-list")


def sample_borrowing(user: get_user_model(), **params):
    book = Book.objects.create(title="title", author="test author", cover="soft", inventory=1, daily_fee=1)
    defaults = {
        "expected_return_date": datetime(2100, 1, 1),
        "book": book,
        "user": user
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass1",
        )

    def test_list_forbidden(self):
        res = self.client.get(BORROWING_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass1",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowings(self):
        sample_borrowing(self.user)
        sample_borrowing(self.user)
        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.order_by("id")
        serializer = BorrowListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_only_users_borrowings(self):
        user = get_user_model().objects.create_user(
            "test1@test.com",
            "testpass1",
        )
        sample_borrowing(self.user)
        sample_borrowing(user)

        res = self.client.get(BORROWING_URL)
        users_borrowings = Borrowing.objects.filter(user=self.user.id)
        serializer_user = BorrowListSerializer(users_borrowings, many=True)

        all_borrowings = Borrowing.objects.all()
        serializer_all = BorrowListSerializer(all_borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer_user.data)
        self.assertNotEqual(res.data, serializer_all.data)


class AdminBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass1",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_filter_borrowing_by_is_active(self):
        borrowing1 = sample_borrowing(self.user, actual_return_date=datetime(2020, 12, 1), )
        borrowing2 = sample_borrowing(self.user)

        res = self.client.get(BORROWING_URL, {"is_active": "true"})

        serializer1 = BorrowListSerializer(borrowing1)
        serializer2 = BorrowListSerializer(borrowing2)

        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer1.data, res.data)

    def test_filter_borrowing_by_user_id(self):
        user = get_user_model().objects.create_user(
            "test1@test.com",
            "testpass1",
        )
        borrowing1 = sample_borrowing(self.user)
        borrowing2 = sample_borrowing(user)

        res = self.client.get(BORROWING_URL, {"user_id": borrowing1.id})

        serializer1 = BorrowListSerializer(borrowing1)
        serializer2 = BorrowListSerializer(borrowing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
