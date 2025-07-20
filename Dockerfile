# Utiliser Python 3.11 slim
FROM python:3.11-slim

# Installer gcc et autres outils nécessaires à la compilation de aiohttp
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

# Définir le dossier de travail
WORKDIR /app

# Copier uniquement requirements.txt en premier (optimisation du cache Docker)
COPY requirements.txt .

# Installer les dépendances
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copier tout le code dans /app
COPY . .

# Lancer ton script principal
CMD ["python", "main.py"]
