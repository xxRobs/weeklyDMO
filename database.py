import os
from sqlmodel import SQLModel, create_engine
from models import PedidoAjuda, Participante

# Lê do ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

# Se quiser colocar opção de fallback
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definida!")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={
        "sslmode": "require"
    },
    pool_pre_ping=True,
    # Se estiver enfrentando problemas com conexões sobrando ou falhas, tente NullPool
    # from sqlalchemy.pool import NullPool
    # poolclass=NullPool
)

def criar_banco():
    SQLModel.metadata.create_all(engine)
