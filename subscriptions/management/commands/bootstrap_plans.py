from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

from subscriptions.models import Plan


class Command(BaseCommand):
    help = "Crée le site Django par défaut et les plans d'abonnement de base."

    def handle(self, *args, **options):
        site, _ = Site.objects.get_or_create(pk=1)
        site.domain = "localhost:8000"
        site.name = "GetExpertCompta"
        site.save()
        self.stdout.write(self.style.SUCCESS("Site Django configuré."))

        defaults = [
            ("premium-weekly", "Premium hebdomadaire", Plan.BillingPeriod.WEEKLY, 5000),
            ("premium-monthly", "Premium mensuel", Plan.BillingPeriod.MONTHLY, 15000),
            ("premium-quarterly", "Premium trimestriel", Plan.BillingPeriod.QUARTERLY, 40000),
            ("premium-yearly", "Premium annuel", Plan.BillingPeriod.YEARLY, 120000),
        ]
        for code, name, period, cents in defaults:
            Plan.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "billing_period": period,
                    "amount_cents": cents,
                    "currency": "XOF",
                    "is_active": True,
                },
            )
        self.stdout.write(self.style.SUCCESS("Plans d'abonnement synchronisés."))
