import pytest

from tracker.models import Transaction


@pytest.mark.django_db
def test_queryset_get_income_method(transactions):
    qs = Transaction.objects.get_income()

    assert qs.count() > 0
    assert all(transaction.transaction_type == "income" for transaction in qs)


@pytest.mark.django_db
def test_queryset_get_expenses_method(transactions):
    qs = Transaction.objects.get_expenses()

    assert qs.count() > 0
    assert all(transaction.transaction_type == "expense" for transaction in qs)


@pytest.mark.django_db
def test_queryset_get_total_income_method(transactions):
    total_income = Transaction.objects.get_total_income()
    assert total_income == sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "income"
    )

@pytest.mark.django_db
def test_queryset_get_total_expenses_method(transactions):
    total_expenses = Transaction.objects.get_total_expenses()
    assert total_expenses == sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "expense"
    )
