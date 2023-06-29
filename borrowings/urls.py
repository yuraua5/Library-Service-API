from rest_framework import routers

from borrowings.views import BorrowViewSet

router = routers.DefaultRouter()
router.register("borrowings", BorrowViewSet)

urlpatterns = router.urls

app_name = "borrowings"
