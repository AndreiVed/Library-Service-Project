from rest_framework import serializers

from books.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingUserSerializer(serializers.ModelSerializer):
    borrow_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    expected_return_date = serializers.DateField(format="%Y-%m-%d")
    actual_return_date = serializers.DateField(format="%Y-%m-%d")
    book = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "is_active",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    expected_return_date = serializers.DateField(format="%Y-%m-%d")
    # actual_return_date = serializers.DateField(format="%Y-%m-%d")
    # book = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            # "actual_return_date",
            "book",
            # "is_active",
        ]


class BorrowingUserRetrieveSerializer(BorrowingUserSerializer):
    book = BookSerializer(many=False, read_only=True)


class BorrowingAdminListSerializer(serializers.ModelSerializer):
    borrow_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    expected_return_date = serializers.DateField(format="%Y-%m-%d")
    actual_return_date = serializers.DateField(format="%Y-%m-%d")
    book = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "is_active",
        ]


class BorrowingAdminRetrieveSerializer(BorrowingAdminListSerializer):
    book = BookSerializer(many=False, read_only=True)
