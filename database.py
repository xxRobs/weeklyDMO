from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///banco.db"
engine = create_engine(DATABASE_URL, echo=True)

def criar_banco():
    SQLModel.metadata.create_all(engine)
