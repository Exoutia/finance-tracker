import random

from django.core.management.base import BaseCommand
from faker import Faker

from tracker.models import Category, Transaction, User


class Command(BaseCommand):
    help = "Generate tranasaction logs for testing"

    def handle(self, *args, **kwargs):
        fake = Faker()
        Faker.seed('coding django is great')

        # Create some cateogires
        categories = [
            "Bills",
            "Food",
            "Shopping",
            "Housing",
            "Salary",
            "Social",
            "Misc",
            "Travel",
            "Rsitedar",
        ]

        for category in categories:
            Category.objects.get_or_create(name=category)

        user = User.objects.filter(username="raven").first()

        if not user:
            user = User.objects.create_superuser(username="raven", password="test") 

        categories = Category.objects.all()
    

        user_id = user

        for _ in range(20):
            Transaction.objects.create(
                category=random.choice(categories),
                user=user_id,
                amount=random.uniform(1, 25000),
                date=fake.date_between(start_date="-1y"),
                transaction_type=random.choice(Transaction.TRANSACTION_TYPE_CHOICES)[0],
            )
