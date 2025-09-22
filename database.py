from sqlmodel import SQLModel, create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
        "sslmode": "require",            # ← Essencial para Supabase
        "client_encoding": "utf8"        # ← Correção do seu erro!
    }
)

def criar_banco():
    SQLModel.metadata.create_all(engine)
