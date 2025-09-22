from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from models import PedidoAjuda
from database import engine, criar_banco


# Senha para finalização
FINALIZACAO_SENHA = "dmomaster"  

# Inicializa a aplicação FastAPI
app = FastAPI()

# Cria o banco e as tabelas, se necessário
criar_banco()

# Configura os diretórios de templates e arquivos estáticos (CSS)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota principal (formulário de envio)
@app.get("/", response_class=HTMLResponse)
def formulario(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Rota que recebe os dados do formulário
@app.post("/enviar", response_class=HTMLResponse)
def receber_dados(
    request: Request,
    nick: str = Form(...),
    precisa_ajuda: bool = Form(...),
    dia_semana: str = Form(...),
    horario: str = Form(...),
    descricao: str = Form(...)
):
    # Cria um novo pedido com os dados recebidos
    novo_pedido = PedidoAjuda(
        nick=nick,
        precisa_ajuda=precisa_ajuda,
        dia_semana=dia_semana,
        horario=horario,
        descricao=descricao
    )

    # Salva no banco de dados
    with Session(engine) as session:
        session.add(novo_pedido)
        session.commit()

    # Redireciona para a lista de pedidos
    return RedirectResponse(url="/lista", status_code=303)

# Rota para listar pedidos ainda não finalizados
@app.get("/lista", response_class=HTMLResponse)
def listar_pedidos(request: Request):
    with Session(engine) as session:
        pedidos = session.exec(
            select(PedidoAjuda).where(PedidoAjuda.finalizado == False)
        ).all()
    return templates.TemplateResponse("lista.html", {"request": request, "pedidos": pedidos})

# Rota para finalizar um pedido
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

# Inicia o servidor Uvicorn ao executar diretamente
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
