Documentation de l'Application de Calculatrice NPI

Exécution de l'Application 

Backend (Python)

Installer les dépendances :
pip install -r requirements.txt

Exécuter le backend :
uvicorn main:app --reload

Frontend (React)

Installer les modules Node :
npm install

Exécuter l'application :
npm start

Tests Unitaires avec Pytest

Naviguer vers le répertoire parent :
cd ..

Exécuter les tests :
pytest

Docker
Pour exécuter la partie backend avec Docker, suivez les étapes suivantes :

Construire les images Docker :
docker-compose build

Démarrer les conteneurs :
docker-compose up
