from django.urls import path

from user.views import (
    CreateUserView,
    ManageUserView,
    TokenObtainPairViewExtended,
    TokenRefreshViewExtended,
    TokenVerifyViewExtended,
)

app_name = "user"

urlpatterns = [
    path("", CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairViewExtended.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshViewExtended.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyViewExtended.as_view(), name="token_verify"),
    path("me/", ManageUserView.as_view(), name="manage"),
]
