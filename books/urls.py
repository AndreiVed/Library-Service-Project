from django.urls import path, include
from rest_framework import routers

from books.views import BookViewSet

app_name = "books"

router = routers.DefaultRouter()
router.register("", BookViewSet)

urlpatterns = [path("", include(router.urls))]
