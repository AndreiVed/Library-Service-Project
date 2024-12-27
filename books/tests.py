from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOK_URL = reverse("books:book-list")


def retrieve_url(url_name, instance_id):
    return reverse(f"books:{url_name}-detail", args=(instance_id,))


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


def _test_book_list(self):
    sample_book()
    res = self.client.get(BOOK_URL)
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    self.assertEqual(res.data, serializer.data)
    self.assertEqual(res.status_code, status.HTTP_200_OK)


class UnauthenticatedBookTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_anauth_book_list(self):
        _test_book_list(self)


class AuthenticatedBookTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_auth_book_list(self):
        _test_book_list(self)

    def test_create_book_forbidden(self):
        payload = {
            "title": "book",
            "author": "author",
            "cover": "soft",
            "inventory": 1,
            "daily_fee": 1,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_forbidden(self):
        book = sample_book()
        payload = {"title": "new_title"}
        res = self.client.patch(retrieve_url("book", book.id), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_forbidden(self):
        book = sample_book()
        res = self.client.delete(retrieve_url("book", book.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(self.admin)

    def test_auth_book_list(self):
        _test_book_list(self)

    def test_create_book_forbidden(self):
        payload = {
            "title": "book",
            "author": "author",
            "cover": "SOFT",
            "inventory": 1,
            "daily_fee": 1,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_book_forbidden(self):
        book = sample_book()
        payload = {"title": "new_title"}
        res = self.client.patch(retrieve_url("book", book.id), payload)
        new_book = Book.objects.get(id=book.id)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(payload["title"], new_book.title)

    def test_delete_book_forbidden(self):
        book = sample_book()
        book_count = Book.objects.count()
        self.assertEqual(book_count, 1)
        res = self.client.delete(retrieve_url("book", book.id))
        book_count = Book.objects.count()
        self.assertEqual(book_count, 0)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
