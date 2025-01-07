from django.utils.timezone import now

from django.db import models

from Library_service_project import settings
from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrows",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrows",
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.borrow_date}, {self.book}, {self.user}"

    def return_book(self):
        if self.is_active:
            self.is_active = False
            self.actual_return_date = now()
            self.book.inventory += 1
            self.book.save()
            self.save()
        else:
            raise ValueError("This borrowing is already returned")

    class Meta:
        ordering = ["-borrow_date"]
