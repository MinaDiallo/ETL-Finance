# ETL-Finance

Pipeline ETL (Extract, Transform, Load) pour l'analyse de données financières.

## Description

Ce projet implémente un pipeline de données complet pour extraire des données financières de diverses sources (Yahoo Finance, Alpha Vantage), les transformer en utilisant PySpark, et les charger dans une base de données PostgreSQL pour analyse et visualisation.

## Fonctionnalités

- Extraction de données de marché depuis Yahoo Finance et Alpha Vantage
- Nettoyage et transformation des données avec PySpark
- Calcul d'indicateurs techniques et fondamentaux
- Stockage dans PostgreSQL
- Visualisation avec Tableau/Power BI
- Orchestration avec Apache Airflow

## Structure du projet

```
etl-finance/
├── config/               # Fichiers de configuration
├── dags/                 # DAGs Airflow
├── data/                 # Données brutes et transformées
├── docker/               # Fichiers Docker
├── notebooks/            # Jupyter notebooks pour l'exploration
├── sql/                  # Scripts SQL
├── src/                  # Code source
│   ├── extraction/       # Extraction de données
│   ├── transformation/   # Transformation avec PySpark
│   ├── loading/          # Chargement dans PostgreSQL
│   └── utils/            # Utilitaires
├── tests/                # Tests unitaires et d'intégration
├── visualization/        # Fichiers de visualisation
├── .gitignore            # Fichiers à ignorer par Git
├── docker-compose.yml    # Configuration Docker Compose
├── Dockerfile            # Dockerfile principal
├── README.md             # Ce fichier
└── requirements.txt      # Dépendances Python
```

## Prérequis

- Python 3.10+
- Docker et Docker Compose
- Clés API pour Yahoo Finance et Alpha Vantage

## Installation

1. Cloner le dépôt :
   ```
   git clone https://github.com/votre-nom-utilisateur/etl-finance.git
   cd etl-finance
   ```

2. Créer les fichiers de configuration :
   ```
   cp config/credentials.yml.example config/credentials.yml
   # Éditer credentials.yml avec vos clés API
   ```

3. Lancer l'environnement Docker :
   ```
   docker-compose up -d
   ```

## Utilisation

1. Accéder à l'interface Airflow : http://localhost:8080
2. Activer les DAGs pour exécuter le pipeline
3. Accéder à PgAdmin pour explorer les données : http://localhost:5050
4. Utiliser Jupyter pour l'analyse interactive : http://localhost:8888

## Licence

