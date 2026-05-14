
# GetExpertCompta

Plateforme SaaS **Django 5** + **DRF** + **PostgreSQL** + **Redis/Celery** pour connecter entreprises et experts-comptables certifiés (PRD dans `instruction.md`).

## Prérequis

- Python **3.12+** (testé avec 3.13)
- PostgreSQL **16** (recommandé en production)
- Redis **7**
- Docker / Docker Compose (optionnel)

## Installation locale (venv)

```powershell
cd c:\GetExpertCompta
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Configurer `.env` : au minimum `SECRET_KEY`, `DATABASE_URL` (PostgreSQL), `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`.

### Migrations

```powershell
$env:DJANGO_SETTINGS_MODULE="getexpertcompta.settings.development"
.\venv\Scripts\python manage.py migrate
.\venv\Scripts\python manage.py bootstrap_plans
```

### Superutilisateur (rôle admin)

```powershell
.\venv\Scripts\python manage.py createsuperuser
```

Le modèle utilisateur impose l’e-mail comme identifiant ; le rôle **admin** est appliqué automatiquement pour les superusers.

### Lancement développement

Terminal 1 — API + site :

```powershell
.\venv\Scripts\python manage.py runserver
```

Terminal 2 — Celery worker :

```powershell
.\venv\Scripts\celery -A getexpertcompta worker -l info
```

Terminal 3 — Celery beat (tâches planifiées, ex. rappels d’abonnement) :

```powershell
.\venv\Scripts\celery -A getexpertcompta beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Configurer les tâches périodiques dans l’admin Django (`django_celery_beat`) en pointant vers `subscriptions.tasks.notify_subscriptions_expiring_soon`.

### Fichiers statiques (production)

```powershell
.\venv\Scripts\python manage.py collectstatic --noinput
```

## Docker Compose

```powershell
copy .env.example .env
docker compose build
docker compose up -d
```

Services : `db` (PostgreSQL), `redis`, `web` (Gunicorn), `celery_worker`, `celery_beat`. Migrations et `collectstatic` sont exécutés au démarrage du conteneur `web` via `scripts/docker-entrypoint-web.sh`.

## API

- Schéma OpenAPI : `/api/schema/`
- Swagger UI : `/api/docs/`
- JWT : `POST /api/v1/auth/token/`, `POST /api/v1/auth/token/refresh/`

## Architecture applicative

`accounts`, `experts`, `businesses`, `subscriptions`, `payments`, `reviews`, `requests_system`, `notifications`, `dashboard`, `adminpanel`, `core`, `api`.

## Déploiement production (recommandations)

- Variables d’environnement strictes (`DEBUG=False`, `SECRET_KEY` fort, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, HTTPS).
- Terminaison TLS devant **Nginx** ou équivalent ; en-têtes `X-Forwarded-Proto`.
- **Gunicorn** + workers adaptés au CPU ; timeouts cohérents avec les paiements.
- Base **PostgreSQL** managée, sauvegardes automatiques et tests de restauration.
- **Redis** dédié pour broker Celery et optionnellement cache.
- Stockage médias sur **S3 compatible** (à brancher via `django-storages` si besoin).
- Surveillance (logs structurés, métriques, alertes sur erreurs 5xx et files Celery).

## Sécurité (résumé)

- RBAC par rôle (`admin`, `business`, `expert`) + permissions DRF dédiées.
- **CSRF** sur les vues session ; JWT pour l’API stateless.
- En-têtes **XSS** / **clickjacking** / **MIME sniffing** ; cookies `HttpOnly` / `Secure` en prod.
- Mots de passe : validateurs Django (longueur ≥ 12) ; PBK2 par défaut.
- **django-axes** : limitation des tentatives de connexion.
- **Throttling** DRF (`anon`, `user`, `auth`, `burst`).
- **Audit** append-only (`core.AuditLog`) sur événements sensibles (connexion, paiements, etc.).
- Téléversements : extension, taille, **MIME** (python-magic ; en prod exiger la détection MIME).
- Paiements : couche d’**adaptateurs** (`payments/services/`) + journalisation ; webhooks à valider par signature (à compléter côté opérateur).

## Prochaines phases de développement

- Intégration réelle des APIs **Orange Money / Wave / Malitel** (webhooks signés, idempotence bout-en-bout).
- **Recherche plein texte PostgreSQL** (`SearchVector` / `GIN`) : le modèle utilise aujourd’hui une recherche `icontains` multi-champs pour rester compatible SQLite en local ; une migration prod peut réintroduire le FTS conformément au PRD.
- Pages légales (CGU, confidentialité, consentement) et export données.
- Tests automatisés (pytest, factories) et pipeline CI (lint + tests + scan dépendances).
- Rate limiting au bord (Nginx / Cloudflare) en complément de DRF.

## Licence

Projet applicatif — définir la licence selon votre entité.
