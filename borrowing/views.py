from django.core.exceptions import RequestAborted
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
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


@extend_schema_view(
    list=extend_schema(
        summary="List borrowings",
        description=(
            "Retrieve a list of borrowings. "
            "Staff users can filter by `user_id` and `is_active`."
        ),
        parameters=[
            OpenApiParameter(
                name="user_id",
                type={"type": "integer"},
                description="Filter borrowings by user ID (staff only).",
            ),
            OpenApiParameter(
                name="is_active",
                type={"type": "string", "enum": ["true", "false"]},
                description=(
                    "Filter borrowings by active status. "
                    "Use 'true' or 'false' as values."
                ),
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve a borrowing",
        description="Retrieve details of a specific borrowing.",
    ),
    create=extend_schema(
        summary="Create a borrowing",
        description="Create a new borrowing for the authenticated user.",
        request=BorrowingCreateSerializer,
        responses={201: BorrowingCreateSerializer},
    ),
)
class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    """
    Borrowing API ViewSet to manage borrowings.

    - Regular users can list and retrieve their borrowings.
    - Staff users can list, retrieve, and filter all borrowings.
    """

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

    @extend_schema(
        summary="Return a borrowed book",
        description=(
            "Mark a book as returned. "
            "This operation is available only for staff users."
        ),
        responses={
            200: OpenApiParameter(
                name="detail", type={"type": "string"}, description="Success message"
            ),
            400: OpenApiParameter(
                name="detail", type={"type": "string"}, description="Error message"
            ),
        },
    )
    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        """
        Custom action to mark a borrowed book as returned.
        """
        borrowing = self.get_object()
        try:
            borrowing.return_book()
            return Response(
                {"detail": "Book successfully returned"},
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
