# Car Fleet Management

Car Fleet Management est une API backend développée avec [FastAPI](https://fastapi.tiangolo.com/) pour la gestion de flotte automobile. Le projet permet de suivre les véhicules, leurs entretiens, les pleins de carburant, et de générer des alertes automatiques selon le kilométrage ou les échéances — avec une gestion **multi-entreprises** et un système de **rôles utilisateurs**.

## Description

L'API centralise la gestion des véhicules d'une flotte : création, modification, suppression, consultation, suivi détaillé des entretiens (vidange, pneus, freins, révision, contrôle technique) et des pleins de carburant. Des alertes sont générées automatiquement pour anticiper les opérations de maintenance.

Le projet gère plusieurs **entreprises isolées entre elles** (multi-tenant) : chaque entreprise dispose de sa propre flotte, de ses propres utilisateurs et de ses propres données, sans visibilité croisée. Un système de **rôles** (administrateur, gestionnaire...) permet de définir précisément qui peut consulter, créer ou modifier quoi au sein de chaque entreprise.

## Philosophie métier

L'API est conçue autour de règles métier explicites :

- le kilométrage est une donnée critique et strictement croissante
- les alertes sont calculées dynamiquement à partir des usages réels
- les opérations de maintenance sont anticipées, pas seulement constatées
- les données de chaque entreprise restent strictement isolées de celles des autres
- les droits d'action dépendent du rôle de l'utilisateur, vérifiés à chaque opération sensible

## Fonctionnalités

- CRUD véhicules (création, lecture, modification, suppression)
- Gestion multi-entreprises : chaque entreprise gère sa propre flotte et ses utilisateurs, de manière isolée
- Système de rôles et permissions : contrôle d'accès fin par ressource (véhicules, entretiens, carburant, utilisateurs, affectations) selon le rôle de l'utilisateur
- Affectation de véhicules à des utilisateurs
- Gestion des entretiens : vidange, pneus, freins, révision, contrôle technique
- Suivi des pleins de carburant (date, km, litres, coût) et statistiques associées
- Calculs et alertes automatiques selon le kilométrage ou la date, avec un moteur d'alertes dédié par type d'entretien
- Authentification sécurisée
- Pagination et filtres sur les historiques d'entretiens
- Architecture modulaire (routers, services, permissions, alertes)

## Qualité et tests

Le projet est couvert par une suite de tests automatisés (Pytest), avec une **couverture de code de 96%** sur l'ensemble du projet, vérifiée via `pytest-cov`. La majorité des modules métier (modèles, routers, permissions, services d'alertes) atteignent 90 à 100% de couverture.

```bash
pytest --cov=app tests/
```

## Stack technique

- Python 3.11+
- FastAPI
- SQLModel / SQLAlchemy
- PostgreSQL (ou SQLite pour les tests)
- Pydantic
- Pytest / pytest-cov pour les tests et la mesure de couverture

## Installation

1. **Cloner le dépôt**

   ```bash
   git clone <votre-url-repo>
   cd Car-Fleet-Managment
   ```

2. **Créer un environnement virtuel**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer la base de données**

   Copier `.env.example` en `.env` et renseigner `DATABASE_URL` (ex : `postgresql://user:password@localhost/dbname`).

## Lancement de l'API

```bash
uvicorn app.main:app --reload
```

L'API est disponible sur `http://localhost:8000`.
La documentation interactive est accessible sur `/docs`.

## Lancer les tests

```bash
# Lancer la suite de tests
pytest

# Avec mesure de couverture
pytest --cov=app tests/

# Rapport détaillé (lignes non couvertes)
pytest --cov=app --cov-report=term-missing tests/
```

## Structure du projet

```
app/
  main.py                    # Point d'entrée FastAPI
  models.py                  # Modèles SQLModel (Véhicule, Entretien, Entreprise, Utilisateur, etc.)
  schemas.py                 # Schémas Pydantic (entrée/sortie API)
  database.py                 # Connexion et session DB
  enums.py                    # Types d'entretiens (Enum)
  security.py                 # Sécurité (hashage, tokens)
  deps/
    auth.py                    # Dépendances d'authentification
  permissions/                 # Contrôle d'accès par ressource et par rôle
    companies.py
    entretiens.py
    fuel.py
    users.py
    vehicule_assignement.py
    vehicules.py
  routers/                     # Routes API (véhicules, entretiens, carburant, utilisateurs, entreprises, affectations, alertes)
  services/
    alerts/                     # Moteur d'alertes, un module dédié par type d'entretien
    entretien_validation.py
    fuel_services.py
    fuel_stats.py
    vehicule_assignment_service.py
  utils/                        # Fonctions utilitaires par domaine
tests/                          # Tests unitaires et d'intégration (couverture 96%)
```

## Extensions futures possibles

- Suivi kilométrique fiable basé sur les pleins et entretiens
- Gestion des incidents et réparations
- Export des données (CSV, PDF)
- Statistiques avancées (coûts, consommation, alertes) à l'échelle d'une entreprise
- Interface web ou mobile dédiée
- Les entretiens sont actuellement exposés uniquement dans le contexte véhicule

---

**Auteur** : Kévin Fruchon (sangoaz)
**Licence** : MIT
