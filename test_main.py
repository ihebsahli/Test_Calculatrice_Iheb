from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from npi_calculator.main import app, Base, get_db
import pytest

# Configurer une base de données de test SQLite en mémoire
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables dans la base de données de test
Base.metadata.create_all(bind=engine)

# Dépendance de test pour remplacer la base de données dans les tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# Test de la route GET "/"
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Calculatrice NPI API"}

# Test de la route POST "/calculate" avec une expression valide
def test_calculate_valid_expression():
    response = client.post("/calculate", json={"expression": ["3", "4", "+"]})
    assert response.status_code == 200
    assert response.json() == {"result": 7}

# Test de la route POST "/calculate" avec une expression invalide
def test_calculate_invalid_expression():
    response = client.post("/calculate", json={"expression": ["3", "+"]})
    assert response.status_code == 200
    assert "error" in response.json()
    assert response.json()["error"] == "Invalid expression format."

# Test de la route POST "/calculate" avec division par zéro
def test_calculate_division_by_zero():
    response = client.post("/calculate", json={"expression": ["4", "0", "/"]})
    assert response.status_code == 200
    assert "error" in response.json()
    assert response.json()["error"] == "Division by zero."

# Test de l'exportation CSV avec une seule opération
def test_export_csv_single_operation():
    # Ajouter une opération
    client.post("/calculate", json={"expression": ["3", "4", "+"]})
    
    # Exporter les données en CSV
    response = client.get("/export-csv")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=operations.csv"
    csv_content = response.content.decode("utf-8")
    assert "id,expression,result\n" in csv_content
    assert "1,3 4 +,7\n" in csv_content

# Test de l'exportation CSV sans opération
def test_export_csv_no_operations():
    response = client.get("/export-csv")
    assert response.status_code == 200
    csv_content = response.content.decode("utf-8")
    assert "id,expression,result\n" in csv_content
    assert len(csv_content.strip()) == len("id,expression,result")
