FROM python:3.11-slim

# Répertoire de travail
WORKDIR /app

# Copier les fichiers de ton projet
COPY . /app

# Installer pip et dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Commande de démarrage
CMD ["python", "main.py"]
