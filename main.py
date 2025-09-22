from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from models import PedidoAjuda, Participante
from database import engine, criar_banco


# Senha para finalização
FINALIZACAO_SENHA = "dmomaster"  

# Inicializa a aplicação FastAPI
app = FastAPI()
criar_banco()

# Configura diretórios de templates e arquivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Página inicial com o formulário
@app.get("/", response_class=HTMLResponse)
def formulario(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Recebe os dados do formulário e cria um novo pedido
@app.post("/enviar", response_class=HTMLResponse)
def receber_dados(
    request: Request,
    nick: str = Form(...),
    precisa_ajuda: str = Form(...),  # recebido como string do formulário
    dia_semana: str = Form(...),
    horario: str = Form(...),
    descricao: str = Form(...)
):
    # Converte string para booleano
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

# Lista os pedidos não finalizados + participantes por pedido
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

# Adiciona membro à PT de um pedido, limitado a 3 participantes
@app.post("/participar/{pedido_id}")
def participar_pedido(pedido_id: int, nick: str = Form(...)):
    with Session(engine) as session:
        # Verifica se o pedido aceita participantes
        pedido = session.get(PedidoAjuda, pedido_id)
        if not pedido or pedido.precisa_ajuda != 0:
            return HTMLResponse(
                "<h2>Este pedido não permite formar PT.</h2>",
                status_code=403
            )

        # Verifica quantos já estão na PT
        count = session.exec(
            select(Participante).where(Participante.pedido_id == pedido_id)
        ).all()

        if len(count) >= 3:
            return HTMLResponse(
                "<h2>Limite de participantes por PT atingido.</h2>",
                status_code=400
            )

        participante = Participante(nick=nick, pedido_id=pedido_id)
        session.add(participante)
        session.commit()

    return RedirectResponse(url="/lista", status_code=303)

# Finaliza um pedido com senha
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

# Roda o servidor Uvicorn localmente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
