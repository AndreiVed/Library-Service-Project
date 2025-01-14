from datetime import timedelta
from unittest.mock import patch

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

        self.assertEqual(self.book.inventory, 0)

    def test_create_borrowing_if_book_inventory_is_zero(self):
        """
        test check what user can take a book and book inventory increases by 1
        """
        book = sample_book(inventory=0)
        payload = {
            "book": book.id,
            "user": self.user.id,
            "expected_return_date": EXPECTED_RETURN_DATE,
        }
        response = self.client.post(URL_BORROWING_LIST, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.book.refresh_from_db()

    def test_return_book(self):
        """
        test check what user can return the book and book inventory increases by 1
        """
        url = reverse(
            "borrowing:borrowing-return-book", kwargs={"pk": self.borrowing.id}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Book successfully returned")

        self.borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertFalse(self.borrowing.is_active)
        self.assertEqual(self.book.inventory, 2)

    def test_return_book_twice(self):
        """
        test check what user can not return the book twice
        """
        url = reverse(
            "borrowing:borrowing-return-book", kwargs={"pk": self.borrowing.id}
        )
        self.client.post(url)
        self.borrowing.refresh_from_db()

        response = self.client.post(url)
        self.assertFalse(self.borrowing.is_active)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "This borrowing is already returned")

    def test_user_borrowing_list(self):
        """
        test check what user can see only his borrowings list
        and take empty response if user try to filter borrowings list by not himself`s user_id
        """
        user2 = sample_user(email="user2@test.com")
        sample_borrowing(user=user2)

        res = self.client.get(URL_BORROWING_LIST)
        res1 = self.client.get(URL_BORROWING_LIST, {"user_id": user2.id})
        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingUserSerializer(borrowings, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res1.data, [])

    def test_user_borrowings_filter_by_active(self):
        """
        test check what user can filter borrowings by is_active field
        """
        inactive_borrowing = sample_borrowing(
            user=self.user, book=self.book, is_active=False
        )

        res1 = self.client.get(URL_BORROWING_LIST, {"is_active": "true"})
        res2 = self.client.get(URL_BORROWING_LIST, {"is_active": "false"})

        serializer1 = BorrowingUserSerializer(self.borrowing)
        serializer2 = BorrowingUserSerializer(inactive_borrowing)

        self.assertIn(serializer1.data, res1.data)
        self.assertNotIn(serializer1.data, res2.data)

        self.assertIn(serializer2.data, res2.data)
        self.assertNotIn(serializer2.data, res1.data)

    @patch("borrowing.views.send_telegram_message")
    def test_borrowing_create_sends_notification(self, mock_send_message):
        payload = {
            "book": self.book.id,
            "user": self.user.id,
            "expected_return_date": EXPECTED_RETURN_DATE,
        }
        response = self.client.post(URL_BORROWING_LIST, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        borrowing = Borrowing.objects.get(id=2)
        message = (
            f"New borrowing created:\n"
            f"User: {self.user.email}\n"
            f"Book: {self.book.title}\n"
            f"Expected Return Date: {borrowing.expected_return_date}"
        )

        mock_send_message.assert_called_once_with(message)


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

    def test_admin_filter_by_is_active_and_user_id(self):
        """
        test check what admin can filter borrowings list by "user_id" and "is_active"
        """
        user1 = sample_user()
        user2 = sample_user(email="user2@test.com")
        sample_borrowing(user=user1)
        sample_borrowing(user=user1, is_active=False)

        sample_borrowing(user=user2)
        sample_borrowing(user=user2, is_active=False)

        inactive_borrowings = Borrowing.objects.filter(is_active=False)
        res1 = self.client.get(URL_BORROWING_LIST, {"is_active": "false"})

        borrowings_user1 = Borrowing.objects.filter(user=user1)
        res2 = self.client.get(URL_BORROWING_LIST, {"user_id": user1.id})

        borrowings_user1_active = Borrowing.objects.filter(user=user1, is_active=True)
        res3 = self.client.get(
            URL_BORROWING_LIST, {"user_id": user1.id, "is_active": "true"}
        )

        serializer1 = BorrowingAdminListSerializer(inactive_borrowings, many=True)
        serializer2 = BorrowingAdminListSerializer(borrowings_user1, many=True)
        serializer3 = BorrowingAdminListSerializer(borrowings_user1_active, many=True)

        self.assertEqual(serializer1.data, res1.data)
        self.assertEqual(serializer2.data, res2.data)
        self.assertEqual(serializer3.data, res3.data)
