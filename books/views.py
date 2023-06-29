from rest_framework import viewsets

from books.models import Book
from Library_Service_API.permissions import IsAdminOrReadOnly
from books.pagination import Pagination
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = Pagination
