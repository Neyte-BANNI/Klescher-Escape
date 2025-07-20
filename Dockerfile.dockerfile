FROM python:3.11-slim

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copier tout le code source dans le conteneur
COPY . /app

# Mise à jour de pip et installation des dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Lancer ton script principal
CMD ["python", "main.py"]