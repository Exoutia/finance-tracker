import pytest

from tracker.factory import TransactionFactory, UserFactory


@pytest.fixture
def transactions():
    return TransactionFactory.create_batch(20)


@pytest.fixture
def user_transactions():
    user = UserFactory()
    return TransactionFactory.create_batch(20, user=user)

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def transaction_dict_params(user):
    transaction = TransactionFactory.create(user=user)
    return {
        'transaction_type': transaction.transaction_type,
        'category': transaction.category_id,
        'date': transaction.date,
        'amount': transaction.amount
    }
