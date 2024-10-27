from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import uvicorn


# Initialiser l'application FastAPI
app = FastAPI()

# Configuration de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Configuration de la base de données avec SQLAlchemy
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Définir le modèle de base de données pour les opérations
class Operation(Base):
    __tablename__ = "operations"
    id = Column(Integer, primary_key=True, index=True)
    expression = Column(String, nullable=False)
    result = Column(String, nullable=False)

# Créer les tables dans la base de données
Base.metadata.create_all(bind=engine)

# Dépendance pour obtenir la session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Expression(BaseModel):
    expression: list[str]

# Fonction pour calculer en Notation Polonaise Inverse (NPI)
def calculate_rpn(expression):
    stack = []
    for token in expression:
        if token.isdigit():
            stack.append(int(token))
        else:
            try:
                b = stack.pop()
                a = stack.pop()
            except IndexError:
                raise HTTPException(status_code=400, detail="Invalid expression format.")
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                if b == 0:
                    raise HTTPException(status_code=400, detail="Division by zero.")
                stack.append(a / b)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported operator: {token}")
    if len(stack) != 1:
        raise HTTPException(status_code=400, detail="Invalid expression format.")
    return stack[0]


@app.get("/")
def read_root():
    return {"message": "Calculatrice NPI API"}

# Route pour calculer l'expression en NPI et sauvegarder dans la base de données
@app.post("/calculate")
def calculate(expression: Expression, db: Session = Depends(get_db)):
    try:
        result = calculate_rpn(expression.expression)
    except HTTPException as e:
        return {"error": e.detail}

    new_operation = Operation(expression=" ".join(expression.expression), result=str(result))
    db.add(new_operation)
    db.commit()
    db.refresh(new_operation)
    return {"result": result}


@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    operations = db.query(Operation).all()
    return [{"id": op.id, "expression": op.expression, "result": op.result} for op in operations]

# Route pour supprimer tout l'historique
@app.delete("/history")
def delete_history(db: Session = Depends(get_db)):
    db.query(Operation).delete()
    db.commit()
    return {"message": "Historique supprimé avec succès"}
    
# Route pour exporter les données en CSV
@app.get("/export-csv")
def export_csv(db: Session = Depends(get_db)):
    operations = db.query(Operation).all()

    def iter_csv():
        yield "id,expression,result\n"
        for op in operations:
            yield f"{op.id},{op.expression},{op.result}\n"

    return StreamingResponse(iter_csv(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=operations.csv"})


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
