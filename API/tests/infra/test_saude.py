import time
from http import HTTPStatus

from pydantic import SecretStr

from api_gestao_pessoal.erros import CodigoErro
from api_gestao_pessoal.main import criar_app
from api_gestao_pessoal.settings import Settings

from ..conftest import FabricaCliente

URL_BANCO_INACESSIVEL = "postgresql+psycopg://u:p@127.0.0.1:1/db"
LIMITE_PRONTO_INDISPONIVEL_S = 3


async def test_saude_ativo(
    settings_teste: Settings, criar_cliente: FabricaCliente
) -> None:
    async with criar_cliente(criar_app(settings_teste)) as cliente:
        resposta = await cliente.get("/saude")
    assert resposta.status_code == HTTPStatus.OK
    assert resposta.json() == {"situacao": "ativo"}


async def test_saude_pronto_com_banco(
    settings_teste: Settings, criar_cliente: FabricaCliente
) -> None:
    async with criar_cliente(criar_app(settings_teste)) as cliente:
        resposta = await cliente.get("/saude/pronto")
    assert resposta.status_code == HTTPStatus.OK
    assert resposta.json() == {"situacao": "pronto"}


async def test_saude_pronto_sem_banco(
    settings_teste: Settings, criar_cliente: FabricaCliente
) -> None:
    sem_banco = settings_teste.model_copy(
        update={"DATABASE_URL": SecretStr(URL_BANCO_INACESSIVEL)}
    )
    async with criar_cliente(criar_app(sem_banco)) as cliente:
        inicio = time.monotonic()
        resposta = await cliente.get("/saude/pronto")
        duracao = time.monotonic() - inicio
    assert resposta.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    corpo = resposta.json()
    assert corpo["codigo"] == CodigoErro.SERVICO_INDISPONIVEL
    assert corpo["mensagem"] == "Serviço indisponível."
    assert corpo["campos"] == []
    assert corpo["detalhes"] is None
    assert corpo["id_requisicao"] == resposta.headers["X-Request-ID"]
    assert duracao < LIMITE_PRONTO_INDISPONIVEL_S
