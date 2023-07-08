from django.db import models

from library_service import settings
from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        ordering = ["borrow_date"]

    def __str__(self):
        return self.book.title

    def calculate_total_price(self):
        total_price = (self.expected_return_date - self.borrow_date).days * self.book.daily_fee
        return total_price

