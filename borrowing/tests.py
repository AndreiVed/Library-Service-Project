from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from .models import Book, Borrowing
from django.contrib.auth import get_user_model

from .serializers import (
    BorrowingUserSerializer,
    BorrowingAdminListSerializer,
)

URL_BORROWING_LIST = reverse("borrowing:borrowing-list")
EXPECTED_RETURN_DATE = (
    f"{(now() + timedelta(days=5)).strftime("%Y-%m-%d")}"  # expected_return_date
)


def sample_book(**params):
    defaults = {
        "title": "book",
        "author": "author",
        "cover": "soft",
        "inventory": 1,
        "daily_fee": 1,
    }

    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_user(**params):
    defaults = {"email": "user@test.com", "password": "password1"}

    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def sample_borrowing(**params):
    book = sample_book(title="book1", inventory=2)
    defaults = {
        "book": book,
        "expected_return_date": EXPECTED_RETURN_DATE,
    }

    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingTestBorrowing(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = sample_book()
        self.user = sample_user()
        self.borrowing = sample_borrowing(
            book=self.book,
            user=self.user,
        )

    def test_create_borrowing(self):
        payload = {
            "book": self.book.id,
            "user": self.user.id,
            "expected_return_date": EXPECTED_RETURN_DATE,
        }
        response = self.client.post(URL_BORROWING_LIST, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_borrowings(self):
        response = self.client.get(URL_BORROWING_LIST)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BorrowingUserTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.book = sample_book()
        self.borrowing = sample_borrowing(
            book=self.book,
            user=self.user,
        )
        self.client.force_authenticate(self.user)

    def test_create_borrowing(self):
        """
        test check what user can take a book and book inventory decreases by 1
        """
        payload = {
            "book": self.book.id,
            "user": self.user.id,
            "expected_return_date": EXPECTED_RETURN_DATE,
        }
        response = self.client.post(URL_BORROWING_LIST, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.book.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.book.inventory, 0)

    def test_return_book(self):
        """
        test check what user can return the book and book inventory increases by 1
        """
        url = reverse(
            "borrowing:borrowing-return-book", kwargs={"pk": self.borrowing.id}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        self.borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertFalse(self.borrowing.is_active)
        self.assertEqual(self.book.inventory, 2)

    def test_user_borrowing_list(self):
        """
        test check what user can see only his borrowings list
        """
        user2 = sample_user(email="user2@test.com")
        sample_borrowing(user=user2)

        res = self.client.get(URL_BORROWING_LIST)
        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingUserSerializer(borrowings, many=True)

        self.assertEqual(res.data, serializer.data)


class BorrowingAdminTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = sample_user(
            email="admin@test.test",
            password="testpassword",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(self.admin)

    def test_admin_borrowing_list(self):
        """
        test check what admin can see all borrowings list
        """
        user1 = sample_user()
        user2 = sample_user(email="user2@test.com")
        sample_borrowing(user=user1)
        sample_borrowing(user=user2)

        res = self.client.get(URL_BORROWING_LIST)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingAdminListSerializer(borrowings, many=True)

        self.assertEqual(res.data, serializer.data)
