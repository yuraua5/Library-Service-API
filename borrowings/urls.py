from django.urls import path, include
from rest_framework import routers

from borrowings.views import BorrowViewSet

router = routers.DefaultRouter()
router.register("borrowings", BorrowViewSet)

urlpatterns = [
    path(
        "return/",
        BorrowViewSet.as_view({"post": "return_book"}),
        name="borrowing-return",
    ),
] + router.urls

app_name = "borrowings"
