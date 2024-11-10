from datetime import datetime, timedelta

import pytest
from django.shortcuts import reverse
from pytest_django.asserts import assertTemplateUsed

from tracker.models import Category, Transaction


@pytest.mark.django_db
def test_total_values_appear_in_transactions(user_transactions, client):
    user = user_transactions[0].user

    client.force_login(user)
    total_income = sum(
        transaction.amount
        for transaction in user_transactions
        if transaction.transaction_type == "income"
    )
    total_expenses = sum(
        transaction.amount
        for transaction in user_transactions
        if transaction.transaction_type == "expense"
    )
    net_income = total_income - total_expenses

    response = client.get(reverse("transactions"))

    assert total_expenses == response.context["total_expenses"]
    assert total_income == response.context["total_income"]
    assert net_income == response.context["net_income"]


@pytest.mark.django_db
def test_transactions_type_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)

    # income
    GET_params = {"transaction_type": "income"}
    response = client.get(reverse("transactions"), GET_params)
    qs = response.context["filter"].qs

    for transaction in qs:
        assert transaction.transaction_type == "income"

    # expense
    GET_params = {"transaction_type": "expense"}
    response = client.get(reverse("transactions"), GET_params)
    qs = response.context["filter"].qs

    for transaction in qs:
        assert transaction.transaction_type == "expense"


@pytest.mark.django_db
def test_start_end_date_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)

    # start date
    start_date_cutoff = datetime.now().date() - timedelta(120)

    GET_params = {"start_date": start_date_cutoff}
    response = client.get(reverse("transactions"), GET_params)
    qs = response.context["filter"].qs

    for transaction in qs:
        assert transaction.date >= start_date_cutoff

    # end_date
    end_date_cutoff = datetime.now().date() - timedelta(20)

    GET_params = {"end_date": end_date_cutoff}
    response = client.get(reverse("transactions"), GET_params)
    qs = response.context["filter"].qs

    for transaction in qs:
        assert transaction.date <= end_date_cutoff


@pytest.mark.django_db
def test_category_type_filter(user_transactions, client):
    user = user_transactions[0].user
    client.force_login(user)

    # single_category test
    category_pks = Category.objects.all()[:2].values_list("pk", flat=True)

    GET_params = {"category_type": category_pks}
    response = client.get(reverse("transactions"), GET_params)
    qs = response.context["filter"].qs

    for transaction in qs:
        assert transaction.category.pk in category_pks


@pytest.mark.django_db
def test_add_transaction_request(user, transaction_dict_params, client):
    client.force_login(user)
    user_transaction_count = Transaction.objects.filter(user=user).count()

    # send request with transaction data

    headers = {"HTTP_HX-Request": "true"}
    response = client.post(
        reverse("create-transaction"), transaction_dict_params, **headers
    )

    assert Transaction.objects.filter(user=user).count() == user_transaction_count + 1

    assertTemplateUsed(response, "tracker/partials/transaction-success.html")


@pytest.mark.django_db
def test_cannot_add_trnsactiond_with_negative_number(
    user, transaction_dict_params, client
):
    client.force_login(user)
    user_transaction_count = Transaction.objects.filter(user=user).count()

    transaction_dict_params["amount"] = -100

    response = client.post(
        reverse("create-transaction"),
        transaction_dict_params,
    )

    assert user_transaction_count == Transaction.objects.filter(user=user).count()

    assertTemplateUsed(response, "tracker/partials/create-transaction.html")

    assert "HX-Retarget" in response.headers


@pytest.mark.django_db
def test_update_request_view(user, transaction_dict_params, client):
    client.force_login(user)

    assert Transaction.objects.filter(user=user).count() == 1

    transaction = Transaction.objects.first()

    now = datetime.now().date()

    transaction_dict_params["amount"] = 1220
    transaction_dict_params["date"] = now

    response = client.post(
        reverse(
            "update-transaction",
            kwargs={"pk": transaction.pk},
        ),
        transaction_dict_params,
    )
    assert Transaction.objects.filter(user=user).count() == 1
    assert Transaction.objects.filter(user=user).first().amount == 1220
    assert Transaction.objects.filter(user=user).first().date == now
    assertTemplateUsed(response, "tracker/partials/transaction-update-success.html")


@pytest.mark.django_db
def test_delete_request_view_method(user, transaction_dict_params, client):
    client.force_login(user)

    assert Transaction.objects.filter(user=user).count() == 1

    transaction = Transaction.objects.first()

    response = client.delete(
        reverse(
            "delete-transaction",
            kwargs={"pk": transaction.pk},
        ),
    )
    assert Transaction.objects.filter(user=user).count() == 0
    assertTemplateUsed(response, "tracker/partials/transaction-update-success.html")


