from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class PedidoAjuda(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nick: str
    precisa_ajuda: bool
    dia_semana: str
    horario: str
    descricao: str
    criado_em: datetime = Field(default_factory=datetime.utcnow)
    finalizado: bool = Field(default=False)

class Participante(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nick: str
    pedido_id: int = Field(foreign_key="pedidoajuda.id")