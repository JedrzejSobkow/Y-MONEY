from collections import defaultdict
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, CharField, Count, Q, Value, When
from django.views.generic import TemplateView

from apps.transactions.models import Transaction
from apps.users.models import Profile
from apps.wallets.models import Wallet

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "core/home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.select_related("user").get(user=self.request.user)
        wallets = list(
            Wallet.objects.filter(owner=profile, is_active=True).order_by("name")
        )

        related_transactions = Transaction.objects.filter(
            Q(wallet__owner=profile) | Q(recipient_wallet__owner=profile)
        )

        currency_groups = defaultdict(list)
        for wallet in wallets:
            currency_groups[wallet.currency.upper()].append(wallet)

        currency_summaries = []
        for currency, grouped_wallets in sorted(currency_groups.items()):
            balance = sum((wallet.balance for wallet in grouped_wallets), Decimal("0.00"))
            currency_summaries.append(
                {
                    "currency": currency,
                    "wallet_count": len(grouped_wallets),
                    "balance": balance,
                }
            )

        recent_transactions = (
            related_transactions.select_related(
                "wallet",
                "recipient_wallet",
                "recipient_friend__user",
            )
            .prefetch_related("items")
            .annotate(
                direction=Case(
                    When(wallet__owner=profile, then=Value("outgoing")),
                    When(recipient_wallet__owner=profile, then=Value("incoming")),
                    default=Value("unknown"),
                    output_field=CharField(),
                )
            )[:6]
        )

        for transaction in recent_transactions:
            if transaction.direction == "incoming" and transaction.recipient_wallet:
                transaction.display_detail_wallet_id = transaction.recipient_wallet.id
            else:
                transaction.display_detail_wallet_id = transaction.wallet.id

            if transaction.type == Transaction.TransactionType.TRANSFER:
                if transaction.direction == "incoming" and transaction.recipient_wallet:
                    transaction.display_currency = transaction.recipient_wallet.currency.upper()
                else:
                    transaction.display_currency = transaction.wallet.currency.upper()
            else:
                transaction.display_currency = transaction.wallet.currency.upper()

        activity_counts = related_transactions.aggregate(
            total=Count("id"),
            income=Count("id", filter=Q(type=Transaction.TransactionType.INCOME)),
            expense=Count("id", filter=Q(type=Transaction.TransactionType.EXPENSE)),
            transfer=Count("id", filter=Q(type=Transaction.TransactionType.TRANSFER)),
        )

        context["profile"] = profile
        context["wallet_count"] = len(wallets)
        context["currency_summaries"] = currency_summaries
        context["recent_transactions"] = recent_transactions
        context["activity_counts"] = activity_counts
        return context