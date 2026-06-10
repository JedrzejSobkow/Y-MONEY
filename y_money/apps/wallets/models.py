from django.db import models
from django.db.models import Q, Sum, Case, When, F, DecimalField
from apps.core.models import TimeStampedModel
from apps.users.models import Profile
from decimal import Decimal

class Wallet(TimeStampedModel):
    class Currency(models.TextChoices):
        # TODO DO NOT HARDCODE THEM
        PLN = "pln", "Polish Złoty"
        EUR = "eur", "Euro"
        CZK = "czk", "Czech Koruna"
        USD = "usd", "United States dollar"
        
    class WalletType(models.TextChoices):
        # TODO DO NOT HARDCODE THEM
        CASH = "cash", "Cash"
        BANK_ACCOUNT = "bank_account", "Bank Account"
        CREDIT_CARD = "credit_card", "Credit Card"
        SAVINGS = "savings", "Savings"
        INVESTMENT = "investment", "Investment"
        OTHER = "other", "Other"
        
        
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="wallets")
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=12, choices=WalletType.choices, default=WalletType.CASH)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.PLN)
    is_active = models.BooleanField(default=True)
    
    # TODO VERIFY IF INCOME OR OUTCOME
    @property
    def balance(self):
        from apps.transactions.models import Transaction
        
        result = Transaction.objects.filter(
            Q(wallet=self) | Q(recipient_wallet=self)
        ).aggregate(
            total=Sum(
                Case(
                    When(
                        recipient_wallet=self,
                        then=F('items__amount') * (-1)
                    ),
                    default=F('items__amount'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )['total'] or Decimal('0.00')
        
        return result

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "name"], name="unique_wallet"),
            models.UniqueConstraint(fields=["owner"], condition=models.Q(is_default=True), name="unique_default_wallet_per_owner",),
        ]
        
        indexes = [
            models.Index(fields=["owner"])
        ]
        
    def __str__(self):
        return f"{self.name}: {self.balance} {self.currency.upper()}"