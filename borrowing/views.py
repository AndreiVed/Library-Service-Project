from django.core.exceptions import RequestAborted
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingUserSerializer,
    BorrowingAdminListSerializer,
    BorrowingAdminRetrieveSerializer,
    BorrowingUserRetrieveSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Borrowing.objects.select_related("user", "book")

    @staticmethod
    def change_str_bool_to_int(is_active):
        if is_active.lower() == "true":
            return 1
        if is_active.lower() == "false":
            return 0
        else:
            raise RequestAborted("'is_active' must be 'true' or 'false'")

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if not user.is_staff:
            queryset = Borrowing.objects.filter(user=user)

        if user_id:
            queryset = queryset.filter(user_id=int(user_id))

        if is_active:
            try:
                is_active_int = self.change_str_bool_to_int(is_active)
                queryset = queryset.filter(is_active=is_active_int)
            except RequestAborted as e:
                raise RequestAborted(str(e))

        return queryset

    def get_serializer_class(self):
        user = self.request.user

        if user.is_staff:
            if self.action == "list":
                return BorrowingAdminListSerializer
            if self.action == "retrieve":
                return BorrowingAdminRetrieveSerializer

        if not user.is_staff:
            if self.action == "list":
                return BorrowingUserSerializer
            if self.action == "retrieve":
                return BorrowingUserRetrieveSerializer

        return BorrowingCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        borrowing = self.get_object()
        try:
            borrowing.return_book()
            return Response(
                {"detail": "Book successfully returned"},
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
