import os
from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definida!")

engine = create_engine(DATABASE_URL, echo=True)

def criar_banco():
    SQLModel.metadata.create_all(engine)
