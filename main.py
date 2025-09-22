from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from dotenv import load_dotenv
load_dotenv()

from models import PedidoAjuda, Participante
from database import engine, criar_banco


# Senha de finalização de pedidos
FINALIZACAO_SENHA = "dmomaster"

# Inicializa o app FastAPI
app = FastAPI()

# Cria as tabelas no banco PostgreSQL via Supabase
criar_banco()

# Diretórios de templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Formulário inicial
@app.get("/", response_class=HTMLResponse)
def formulario(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Recebe dados do formulário e salva no banco
@app.post("/enviar", response_class=HTMLResponse)
def receber_dados(
    request: Request,
    nick: str = Form(...),
    precisa_ajuda: str = Form(...),
    dia_semana: str = Form(...),
    horario: str = Form(...),
    descricao: str = Form(...)
):
    precisa_ajuda = precisa_ajuda.lower() == "true"

    novo_pedido = PedidoAjuda(
        nick=nick,
        precisa_ajuda=precisa_ajuda,
        dia_semana=dia_semana,
        horario=horario,
        descricao=descricao
    )

    with Session(engine) as session:
        session.add(novo_pedido)
        session.commit()

    return RedirectResponse(url="/lista", status_code=303)

# Lista pedidos não finalizados + membros da PT se aplicável
@app.get("/lista", response_class=HTMLResponse)
def listar_pedidos(request: Request):
    with Session(engine) as session:
        pedidos = session.exec(
            select(PedidoAjuda).where(PedidoAjuda.finalizado == False)
        ).all()

        participantes_por_pedido = {}
        for pedido in pedidos:
            participantes = session.exec(
                select(Participante).where(Participante.pedido_id == pedido.id)
            ).all()
            participantes_por_pedido[pedido.id] = participantes

    return templates.TemplateResponse("lista.html", {
        "request": request,
        "pedidos": pedidos,
        "participantes_por_pedido": participantes_por_pedido
    })

# Adiciona membro à PT, limitado a pedidos que permitem e até 3 pessoas
@app.post("/participar/{pedido_id}")
def participar_pedido(pedido_id: int, nick: str = Form(...)):
    with Session(engine) as session:
        pedido = session.get(PedidoAjuda, pedido_id)
        if pedido.precisa_ajuda:
    # ou seja, precisa de ajuda é True
            return HTMLResponse("<h2>Este pedido não permite formar PT.</h2>", status_code=403)

        count = session.exec(
            select(Participante).where(Participante.pedido_id == pedido_id)
        ).all()

        if len(count) >= 3:
            return HTMLResponse("<h2>Limite de participantes por PT atingido.</h2>", status_code=400)

        participante = Participante(nick=nick, pedido_id=pedido_id)
        session.add(participante)
        session.commit()

    return RedirectResponse(url="/lista", status_code=303)

# Finaliza pedido com senha
@app.post("/finalizar/{pedido_id}")
def finalizar_pedido(pedido_id: int, senha: str = Form(...)):
    if senha != FINALIZACAO_SENHA:
        return HTMLResponse("<h2>Senha incorreta! A finalização foi negada.</h2>", status_code=403)

    with Session(engine) as session:
        pedido = session.get(PedidoAjuda, pedido_id)
        if pedido:
            pedido.finalizado = True
            session.add(pedido)
            session.commit()

    return RedirectResponse(url="/lista", status_code=303)

# Para rodar localmente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
