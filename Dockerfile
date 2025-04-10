FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY . .

# Créer un utilisateur non-root pour exécuter l'application
RUN useradd -m etluser
USER etluser

# Définir la variable d'environnement PYTHONPATH
ENV PYTHONPATH=/app

# Commande par défaut
CMD ["python", "-m", "src.main"]