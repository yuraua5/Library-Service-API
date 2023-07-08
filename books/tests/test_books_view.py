from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOK_URL = reverse("books:book-list")


def sample_book(**params):
    defaults = {
        "title": "title",
        "author": "author",
        "cover": "soft",
        "inventory": 1,
        "daily_fee": 1,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_view(self):
        sample_book()
        sample_book(title="Test book 2")

        res = self.client.get(BOOK_URL)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_detail_view(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_book_forbidden(self):
        payload = {
            "title": "test",
            "author": "author",
            "cover": "soft",
            "inventory": 2,
            "daily_fee": 1
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass1"
        )
        self.client.force_authenticate(self.user)

    def test_delete_book_forbidden(self):
        book = sample_book()

        res = self.client.delete(detail_url(book.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass1",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Book test",
            "author": "Test author",
            "cover": "hard",
            "inventory": 2,
            "daily_fee": 2,
        }

        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_delete_book(self):
        book = sample_book()

        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
