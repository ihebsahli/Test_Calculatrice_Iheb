# Utilisez une image de base Python
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application dans le conteneur
COPY . .

# Installer les dépendances via requirements.txt
RUN pip install -r requirements.txt

# Exposer le port 8000
EXPOSE 8000

# Démarrer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
