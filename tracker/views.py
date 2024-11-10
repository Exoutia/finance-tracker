from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django_htmx.http import retarget

from tracker.charting import (plot_category_pie_chart,
                              plot_income_expneses_bar_chart)
from tracker.forms import TransactionForm
from tracker.resources import TransactionResource

from .filter import TransactionFilter
from .models import Transaction


def index(request):
    return render(request, "tracker/index.html")


@login_required
def transaction_list(request):
    transactions_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related(
            "category"
        ),
    )
    paginator = Paginator(transactions_filter.qs, settings.PAGE_SIZE)
    transaction_page = paginator.page(1)

    total_income = transactions_filter.qs.get_total_income()
    total_expenses = transactions_filter.qs.get_total_expenses()
    net_income = total_income - total_expenses

    context = {
        "transactions": transaction_page,
        "filter": transactions_filter,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_income": net_income,
    }

    if request.htmx:
        return render(request, "tracker/partials/transaction-container.html", context)
    return render(request, "tracker/transaction-list.html", context)


@login_required
def create_transaction(request):

    if request.method == "POST":
        form = TransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            context = {"message": "Transaction added successfully"}
            return render(request, "tracker/partials/transaction-success.html", context)
        else:
            context = {"form": form}
            response = render(
                request, "tracker/partials/create-transaction.html", context
            )
            return retarget(response, "#transaction-block")

    context = {"form": TransactionForm()}
    return render(request, "tracker/partials/create-transaction.html", context)


@login_required
def update_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save()
            context = {"message": "Transaction was updated successfully"}
            return render(
                request,
                "tracker/partials/transaction-update-success.html",
                context,
            )
        else:
            context = {
                "form": form,
                "transaction": transaction,
            }

            response = render(
                request, "tracker/partials/update-transaction.html", context
            )

            return retarget(response, "#transaction-block")

    form = TransactionForm(instance=transaction)
    context = {
        "form": form,
        "transaction": transaction,
    }
    return render(request, "tracker/partials/update-transaction.html", context)


@login_required
@require_http_methods(["DELETE"])
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    context = {
        "message": f"transaction of {transaction.amount} on {transaction.date} of {transaction.transaction_type} type, is deleted successfully",
    }
    return render(
        request,
        "tracker/partials/transaction-update-success.html",
        context,
    )


@login_required
def get_transactions(request):
    page_number = request.GET.get("page", 1)
    transactions_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related(
            "category"
        ),
    )
    paginator = Paginator(transactions_filter.qs, settings.PAGE_SIZE)

    context = {"transactions": paginator.page(page_number)}
    return render(
        request, "tracker/partials/transaction-container.html#transaction_list", context
    )


@login_required
def transaction_charts(request):
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related(
            "category"
        ),
    )

    transactions = transaction_filter.qs
    income_expense_bar = plot_income_expneses_bar_chart(transactions)
    income_pie_chart = plot_category_pie_chart(transactions.filter(transaction_type= "income"))
    expense_pie_chart = plot_category_pie_chart(transactions.filter(transaction_type= "expense"))

    context = {
        "filter": transaction_filter,
        "income_expense_bar": income_expense_bar.to_html(),
        "income_pie_chart": income_pie_chart.to_html(),
        "expense_pie_chart": expense_pie_chart.to_html(),
    }

    if request.htmx:
        return render(request, "tracker/partials/charts-container.html", context)
    
    return render(request, "tracker/charts.html", context)

@login_required
def export_transactions(request):
    if request.htmx:
        return HttpResponse(headers={"HX-Redirect": request.get_full_path()})
    
    transaction_filter = TransactionFilter(
        request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related(
            "category"
        ),
    )

    data = TransactionResource().export(transaction_filter.qs)
    response = HttpResponse(data.csv)
    response['Content-Disposition'] = 'attachment; filename="transaction.csv'
    return response

