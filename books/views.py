from django.shortcuts import render
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from books.models import Book
from books.permissions import IsAdminOrReadOnly
from books.serializers import BookSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List all books",
        description="Retrieve a list of all books in the system. Accessible to all users.",
        responses={
            200: BookSerializer(many=True),
            403: {"description": "Permission denied."},
        },
    ),
    retrieve=extend_schema(
        summary="Retrieve a specific book",
        description="Retrieve detailed information about a book by its ID. Accessible to all users.",
        responses={
            200: BookSerializer,
            404: {"description": "Book not found."},
        },
    ),
    create=extend_schema(
        summary="Create a new book",
        description="Add a new book to the system. Only admins are allowed to perform this action.",
        request=BookSerializer,
        responses={
            201: BookSerializer,
            403: {"description": "Permission denied."},
        },
    ),
    update=extend_schema(
        summary="Update a book",
        description="Fully update the details of a book by its ID. Only admins are allowed to perform this action.",
        request=BookSerializer,
        responses={
            200: BookSerializer,
            403: {"description": "Permission denied."},
            404: {"description": "Book not found."},
        },
    ),
    partial_update=extend_schema(
        summary="Partially update a book",
        description="Update specific fields of a book by its ID. Only admins are allowed to perform this action.",
        request=BookSerializer,
        responses={
            200: BookSerializer,
            403: {"description": "Permission denied."},
            404: {"description": "Book not found."},
        },
    ),
    destroy=extend_schema(
        summary="Delete a book",
        description="Remove a book from the system by its ID. Only admins are allowed to perform this action.",
        responses={
            204: {"description": "No content. Book successfully deleted."},
            403: {"description": "Permission denied."},
            404: {"description": "Book not found."},
        },
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books.

    - Admin users can perform all actions (create, update, delete).
    - Non-admin users can only view books (list, retrieve).
    """

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]
