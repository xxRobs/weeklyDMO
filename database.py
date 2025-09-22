from sqlmodel import SQLModel, create_engine
from models import PedidoAjuda, Participante  # <- certifique-se de importar todos os modelos

# Criar o engine apontando para o banco SQLite
engine = create_engine("sqlite:///banco.db")

def criar_banco():
    SQLModel.metadata.create_all(engine)
