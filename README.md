# Car Fleet Management

Car Fleet Management est une API backend développée avec [FastAPI](https://fastapi.tiangolo.com/) pour la gestion de flotte automobile. Ce projet permet de suivre les véhicules, leurs entretiens, les pleins de carburant et de générer des alertes automatiques selon le kilométrage ou les échéances.

## 🚗 Description

L’API centralise la gestion des véhicules d’une flotte : création, modification, suppression, consultation, suivi détaillé des entretiens (vidange, pneus, freins, révision, contrôle technique) et des pleins de carburant. Des alertes sont générées automatiquement pour anticiper les opérations de maintenance.

## ✨ Fonctionnalités

- CRUD véhicules (création, lecture, modification, suppression)
- Gestion des entretiens : vidange, pneus, freins, révision, contrôle technique
- Suivi des pleins de carburant (date, km, litres, coût)
- Calculs et alertes automatiques selon le kilométrage ou la date
- Pagination et filtres sur les historiques d’entretiens
- Architecture modulaire (routers, services, alerts)

## 🛠️ Stack technique

- Python 3.11+
- FastAPI
- SQLModel / SQLAlchemy
- PostgreSQL (ou SQLite pour les tests)
- Pydantic

## 🚀 Installation

1. **Cloner le dépôt**

   ```sh
   git clone <votre-url-repo>
   cd Car\ Fleet\ Managment\ FastAPI
   ```

2. **Créer un environnement virtuel**

   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**

   ```sh
   pip install -r requirements.txt
   ```

4. **Configurer la base de données**
   - Copier `.env.example` en `.env` et renseigner `DATABASE_URL` (ex : `postgresql://user:password@localhost/dbname`).

## 🏁 Lancement de l’API

```sh
uvicorn app.main:app --reload
```

L’API sera disponible sur [http://localhost:8000](http://localhost:8000)  
La documentation interactive est accessible sur `/docs`.

## 🗂️ Structure du projet

```
app/
 ├── app/main.py           # Point d'entrée FastAPI
 ├── app/models.py         # Modèles SQLModel (Vehicule, Entretien, etc.)
 ├── app/schemas.py        # Schémas Pydantic (entrée/sortie API)
 ├── app/database.py       # Connexion et session DB
 ├── app/enums.py          # Types d'entretiens (Enum)
 ├── routers/              # Routes API (véhicules, entretiens, alertes)
 ├── services/             # Logique métier (alertes, validation)
tests/                     # Tests unitaires et d'intégration
```

## 🔮 Extensions futures possibles

- Authentification et gestion des utilisateurs
- Gestion des incidents et réparations
- Export des données (CSV, PDF)
- Statistiques avancées (coûts, consommation, alertes)
- Interface web ou mobile dédiée

---

**Auteur** : [Sangoaz]  
**Licence** : MIT
