from django.contrib import admin

from tracker.models import Category, Transaction


from unfold.admin import ModelAdmin


@admin.register(Transaction)
class TransactionClass(ModelAdmin):
    pass

@admin.register(Category)
class CategoryClass(ModelAdmin):
    pass
