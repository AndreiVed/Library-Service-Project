from datetime import timedelta
from django.test import TestCase
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse
from .models import Book, Borrowing
from django.contrib.auth import get_user_model

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
    defaults = {"email": "test@test.com", "password": "password"}

    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


# def sample_borrowing(**params):
#     book = sample_book()
#     user = sample_user()
#     defaults = {
#         "book": book.id,
#         "user": user.id,
#         "expected_return_date": EXPECTED_RETURN_DATE,
#     }
#
#     defaults.update(params)
#     return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingTestBorrowing(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book = sample_book()
        self.user = sample_user()
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=EXPECTED_RETURN_DATE,
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
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=EXPECTED_RETURN_DATE,
        )
        self.client.force_authenticate(self.user)

    def test_create_borrowing(self):
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
        url = reverse(
            "borrowing:borrowing-return-book", kwargs={"pk": self.borrowing.id}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        self.borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertFalse(self.borrowing.is_active)
        self.assertEqual(self.book.inventory, 2)

    def test_user_borrow_list(self):
        """
        test check what user can see only his borrowing list
        """
        # TODO create two users, one borrowing for each user,
        # TODO check that count of borrowing in the list equal 1
        # TODO check that borrowing owner is user1
        pass
