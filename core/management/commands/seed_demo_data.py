"""Données de démonstration réalistes (Afrique francophone, experts, entreprises, avis, abonnements)."""

from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from businesses.models import BusinessProfile
from experts.models import ExpertProfile, Specialty
from notifications.models import Notification
from payments.models import PaymentTransaction
from requests_system.models import ServiceRequest, ServiceRequestExpert
from reviews.models import Review
from subscriptions.models import Plan
from subscriptions.services.demo_checkout import activate_demo_subscription


DEMO_EMAIL_DOMAIN = "@demo.getexpertcompta.africa"
DEFAULT_PASSWORD = "Demo2026!Secure"

SPECIALTIES = [
    ("Audit légal & consolidé", "audit-legal"),
    ("Conseil fiscal & TVA", "fiscal-tva"),
    ("Normes OHADA / SYSCOHADA", "ohada"),
    ("Paie & social", "paie-social"),
    ("Contrôle de gestion", "controle-gestion"),
    ("Due diligence & transactions", "due-diligence"),
]

EXPERTS_SEED = [
    ("Amadou", "Diallo", "SN", "Dakar", "Expert-comptable diplômé ONECCA — PME & ONG", 14, ExpertProfile.Availability.AVAILABLE),
    ("Fatou", "Sow", "ML", "Bamako", "CABAC / consolidation — grands comptes", 18, ExpertProfile.Availability.OCCUPIED),
    ("Koffi", "N'Guessan", "CI", "Abidjan", "Fiscalité internationale & transfert pricing", 12, ExpertProfile.Availability.AVAILABLE),
    ("Aminata", "Ouédraogo", "BF", "Ouagadougou", "Secteur agricole & coopératives", 9, ExpertProfile.Availability.UNAVAILABLE),
    ("Jean-Baptiste", "Mvondo", "CM", "Douala", "Transformation digitale & ERP comptable", 11, ExpertProfile.Availability.AVAILABLE),
    ("Mariam", "Traoré", "NE", "Niamey", "Projets Banque mondiale & bailleurs", 16, ExpertProfile.Availability.OCCUPIED),
    ("Essohanam", "Kossi", "TG", "Lomé", "Restructuration & prévention des difficultés", 10, ExpertProfile.Availability.AVAILABLE),
    ("Habib", "Ben Youssef", "MR", "Nouakchott", "Commerce transfrontalier & douanes", 8, ExpertProfile.Availability.AVAILABLE),
]

BUSINESSES_SEED = [
    ("Société Agro-Terre Sahel SARL", "SN", "Thiès"),
    ("Logistique Baoulé CI", "CI", "Yamoussoukro"),
    ("Textile Niger Export", "NE", "Maradi"),
]


class Command(BaseCommand):
    help = "Crée des experts, entreprises, avis, notifications et abonnements de démonstration (domaine *@demo.getexpertcompta.africa)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Supprime d’abord tous les comptes dont l’e-mail se termine par @demo.getexpertcompta.africa.",
        )
        parser.add_argument(
            "--password",
            default=DEFAULT_PASSWORD,
            help="Mot de passe des comptes démo (défaut sécurisé pour environnement local).",
        )

    def handle(self, *args, **options):
        reset: bool = options["reset"]
        password: str = options["password"]

        if reset:
            deleted_counts = User.objects.filter(email__endswith=DEMO_EMAIL_DOMAIN).delete()[0]
            self.stdout.write(self.style.WARNING(f"Objets supprimés en cascade (dont comptes démo) : {deleted_counts}."))

        if User.objects.filter(email__endswith=DEMO_EMAIL_DOMAIN).exists():
            self.stdout.write(self.style.NOTICE("Des comptes démo existent déjà. Utilisez --reset pour repartir de zéro."))
            return

        with transaction.atomic():
            self._seed_plans()
            specs = self._seed_specialties()
            experts = self._seed_experts(password, specs)
            businesses = self._seed_businesses(password)
            main_business = businesses[0]
            main_user = main_business.user
            self._seed_subscription_demo(main_user)
            self._seed_reviews_and_requests(main_business, experts[:5])
            self._seed_notifications(main_user)
            self._verify_emails_all_demo()

        from core.services.free_access import invalidate_free_discovery_cache

        invalidate_free_discovery_cache()
        self.stdout.write(self.style.SUCCESS("Données de démonstration créées avec succès."))

    def _seed_plans(self) -> None:
        plans_data = [
            ("premium-weekly", "Premium Hebdo", Plan.BillingPeriod.WEEKLY, 9_900, "Accès illimité une semaine — idéal pour un audit ciblé."),
            ("premium-monthly", "Premium Mensuel", Plan.BillingPeriod.MONTHLY, 29_900, "Le plus choisi par les PME en croissance."),
            ("premium-quarterly", "Premium Trimestriel", Plan.BillingPeriod.QUARTERLY, 79_900, "Économisez vs mensuel avec engagement 3 mois."),
            ("premium-yearly", "Premium Annuel", Plan.BillingPeriod.YEARLY, 249_900, "Vision long terme — priorité support."),
        ]
        for code, name, period, cents, desc in plans_data:
            Plan.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "billing_period": period,
                    "amount_cents": cents,
                    "currency": "XOF",
                    "is_active": True,
                    "description": desc,
                },
            )

    def _seed_specialties(self) -> dict[str, Specialty]:
        out: dict[str, Specialty] = {}
        for name, slug in SPECIALTIES:
            s, _ = Specialty.objects.get_or_create(slug=slug, defaults={"name": name})
            out[slug] = s
        return out

    def _seed_experts(self, password: str, specs: dict[str, Specialty]) -> list[ExpertProfile]:
        slug_cycle = list(specs.keys())
        experts: list[ExpertProfile] = []
        for i, (fn, ln, country, city, title, years, avail) in enumerate(EXPERTS_SEED):
            email = f"expert{i+1:02d}{DEMO_EMAIL_DOMAIN}"
            bio = (
                f"{fn} accompagne dirigeants et structures en {country} sur les problématiques "
                f"comptables, fiscales et de gouvernance. Interventions en français, expérience terrain."
            )
            user = User.objects.create_user(
                email=email,
                password=password,
                role=User.Role.EXPERT,
                first_name=fn,
                last_name=ln,
                is_active=True,
            )
            ep = ExpertProfile.objects.get(user=user)
            ep.title = title
            ep.country = country
            ep.city = city
            ep.years_experience = years
            ep.bio = bio
            ep.verification_status = ExpertProfile.VerificationStatus.VERIFIED
            ep.availability = avail
            ep.average_rating = Decimal("0")
            ep.review_count = 0
            ep.save()
            ep.specialties.add(specs[slug_cycle[i % len(slug_cycle)]], specs[slug_cycle[(i + 1) % len(slug_cycle)]])
            experts.append(ep)
        return experts

    def _seed_businesses(self, password: str) -> list[BusinessProfile]:
        profiles: list[BusinessProfile] = []
        for idx, (company, country, city) in enumerate(BUSINESSES_SEED):
            email = f"entreprise{idx+1:02d}{DEMO_EMAIL_DOMAIN}"
            user = User.objects.create_user(
                email=email,
                password=password,
                role=User.Role.BUSINESS,
                first_name="Contact",
                last_name=company[:20],
                is_active=True,
            )
            bp = user.business_profile
            bp.company_name = company
            bp.country = country
            bp.city = city
            bp.tax_id = f"DEMO-{country}-{idx+1}"
            bp.phone = f"+221 33 8{idx:02d} 00 00 00"
            bp.save()
            profiles.append(bp)
        return profiles

    def _seed_subscription_demo(self, business_user: User) -> None:
        plan = Plan.objects.filter(code="premium-monthly", is_active=True).first()
        if not plan:
            return
        activate_demo_subscription(
            user=business_user,
            plan=plan,
            provider=PaymentTransaction.Provider.INTERNAL,
            request=None,
        )

    def _seed_reviews_and_requests(self, business: BusinessProfile, experts_slice: list[ExpertProfile]) -> None:
        for i, expert in enumerate(experts_slice):
            sr = ServiceRequest.objects.create(
                business=business,
                country=business.country,
                accounting_needs=(
                    f"Mission démo {i+1} : revue des comptes trimestriels, harmonisation SYSCOHADA, "
                    f"et préparation des états financiers pour levée de fonds."
                ),
                status=ServiceRequest.Status.CLOSED,
                created_by=business.user,
            )
            ServiceRequestExpert.objects.create(
                service_request=sr,
                expert=expert,
                status=ServiceRequestExpert.Status.ACCEPTED,
                responded_at=timezone.now(),
            )
            Review.objects.create(
                service_request=sr,
                business=business,
                expert=expert,
                rating=4 + (i % 2),
                comment=(
                    "Intervention structurante, reporting clair et respect des délais. "
                    "Nous recommandons cet expert pour les dossiers complexes."
                ),
                moderation_status=Review.ModerationStatus.APPROVED,
            )

    def _seed_notifications(self, business_user: User) -> None:
        items = [
            (Notification.EventType.PAYMENT_CONFIRMED, "Paiement confirmé (démo)", "Votre abonnement Premium mensuel est actif."),
            (Notification.EventType.REQUEST_ACCEPTED, "Demande clôturée", "Une mission démo a été marquée comme terminée."),
            (Notification.EventType.GENERIC, "Bienvenue sur GetExpertCompta", "Explorez le catalogue découverte et le tunnel Premium."),
        ]
        for event, title, body in items:
            Notification.objects.create(
                user=business_user,
                event_type=event,
                title=title,
                body=body,
            )

    def _verify_emails_all_demo(self) -> None:
        try:
            from allauth.account.models import EmailAddress
        except Exception:
            return
        for user in User.objects.filter(email__endswith=DEMO_EMAIL_DOMAIN):
            email = user.email.lower()
            EmailAddress.objects.filter(user=user).exclude(email=email).delete()
            ea, created = EmailAddress.objects.get_or_create(
                user=user,
                email=email,
                defaults={"primary": True, "verified": True},
            )
            if not created and (not ea.verified or not ea.primary):
                ea.verified = True
                ea.primary = True
                ea.save()
